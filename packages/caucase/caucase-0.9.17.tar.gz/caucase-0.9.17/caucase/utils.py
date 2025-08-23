# This file is part of caucase
# Copyright (C) 2017-2023  Nexedi SA
#     Alain Takoudjou <alain.takoudjou@nexedi.com>
#     Vincent Pelletier <vincent@nexedi.com>
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.
"""
Caucase - Certificate Authority for Users, Certificate Authority for SErvices

Small-ish functions needed in many places.
"""
from __future__ import absolute_import, print_function
from binascii import a2b_base64, b2a_base64, hexlify
import calendar
import codecs
from collections import defaultdict
import datetime
import email
import json
import os
import sys
import threading
import traceback
import time
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
import cryptography.exceptions
import pem
from .exceptions import (
  CertificateVerificationError,
  NotJSON,
)

if sys.version_info[0] >= 3: # pragma: no cover
  unicode = str

  def getAuthorityKeyIdentifier(cert):
    """
    Returns the authority key identifier of given certificate.
    """
    # pylint: disable=no-member
    return int.from_bytes(_getAuthorityKeyIdentifier(cert), 'big')
    # pylint: enable=no-member
else: # pragma: no cover
  # BBB: py2.7
  def getAuthorityKeyIdentifier(cert):
    """
    Returns the authority key identifier of given certificate.
    """
    return int(_getAuthorityKeyIdentifier(cert).encode('hex'), 16)

DEFAULT_DIGEST_LIST = ('sha256', 'sha384', 'sha512')
DEFAULT_DIGEST = DEFAULT_DIGEST_LIST[0]
DEFAULT_DIGEST_CLASS = getattr(hashes, DEFAULT_DIGEST.upper())
# load-time sanity check
def _checkDefaultDigestsAvailable():
  for x in DEFAULT_DIGEST_LIST:
    getattr(hashes, x.upper())
_checkDefaultDigestsAvailable()
del _checkDefaultDigestsAvailable

_cryptography_backend = default_backend()

# Registration-less OID under 1.3.6.1.4.1.37476.9000 tree (aka ViaThinkSoft
# tree for open source project: https://oidplus.viathinksoft.com )
CAUCASE_OID_TOP = '1.3.6.1.4.1.37476.9000.70.0'
CAUCASE_OID_AUTO_SIGNED = CAUCASE_OID_TOP + '.0'
# Reserved for tests: no meaning, always stripped but never specificaly
# checked for in the code.
CAUCASE_OID_RESERVED = CAUCASE_OID_TOP + '.999'
_CAUCASE_OID_AUTO_SIGNED = x509.oid.ObjectIdentifier(CAUCASE_OID_AUTO_SIGNED)
CAUCASE_POLICY_INFORMATION_AUTO_SIGNED = x509.PolicyInformation(
  _CAUCASE_OID_AUTO_SIGNED,
  [
    x509.UserNotice(
      None,
      'Auto-signed caucase certificate',
    ),
  ]
)
# Registration-less OID under 2.25 tree (aka uuid tree)
# Sadly, many implementations break when encountering 128-bits OIDs, making
# these certificates difficult to use.
CAUCASE_LEGACY_OID_TOP = '2.25.285541874270823339875695650038637483517'
CAUCASE_LEGACY_OID_AUTO_SIGNED = CAUCASE_LEGACY_OID_TOP + '.0'
CAUCASE_LEGACY_OID_RESERVED = CAUCASE_LEGACY_OID_TOP + '.999'
try:
  _CAUCASE_LEGACY_OID_AUTO_SIGNED = x509.oid.ObjectIdentifier(
    CAUCASE_LEGACY_OID_AUTO_SIGNED,
  )
except ValueError: # pragma: no cover
  # cryptography started raising when instanciating long OIDs somewhere up to
  # 40.0.2 .
  _CAUCASE_AUTO_SIGNED_OID_SET = (
    _CAUCASE_OID_AUTO_SIGNED,
  )
else: # pragma: no cover
  _CAUCASE_AUTO_SIGNED_OID_SET = (
    _CAUCASE_OID_AUTO_SIGNED,
    _CAUCASE_LEGACY_OID_AUTO_SIGNED,
  )

def isCertificateAutoSigned(crt):
  """
  Checks whether given certificate was automatically signed by caucase.

  Allows ensuring no rogue certificate could be emitted before legitimate owner
  could take control of their instance: in such case, "first" certificate would
  not appear as auto-signed.

  Returns True if certificate is auto-signed, False otherwise.
  """
  try:
    extension = crt.extensions.get_extension_for_class(
      x509.CertificatePolicies,
    )
  except x509.ExtensionNotFound:
    pass
  else:
    for policy_information in extension.value:
      if policy_information.policy_identifier in _CAUCASE_AUTO_SIGNED_OID_SET:
        return True
  return False

def _getPEMTypeDict(path, result=None):
  if result is None:
    result = defaultdict(list)
  for entry in pem.parse_file(path):
    result[pem.Key if isinstance(entry, pem.Key) else type(entry)].append(
      entry,
    )
  return result

def getCertList(crt_path):
  """
  Return a list of certificates.
  """
  return _getPEMListFromPath(crt_path, pem.Certificate)

def getCRLList(crl_path):
  """
  Return a list of Certificate Revocation Lists.
  """
  return _getPEMListFromPath(crl_path, pem.CertificateRevocationList)

def _getPEMListFromPath(path, pem_type):
  result = []
  for file_name in (
    [os.path.join(path, x) for x in os.listdir(path)]
    if os.path.isdir(path) else
    [path]
  ):
    # path is missing, or a symlink in path (if path is a directory) is broken
    if os.path.exists(file_name) and not os.path.isdir(file_name):
      for pem_object in _getPEMTypeDict(file_name).get(pem_type, ()):
        result.append(pem_object.as_bytes())
  return result

def saveCertList(crt_path, cert_pem_list):
  """
  Store given list of PEM-encoded certificates in given path.

  crt_path (str)
  May point to a directory a file, or nothing.
  If it does not exist, and this value contains an extension, a file is
  created, otherwise a directory is.
  If it is a file, all certificates are written in it.
  If it is a folder, each certificate is stored in a separate file.

  cert_pem_list (list of bytes)
  """
  _savePEMList(crt_path, cert_pem_list, load_ca_certificate, '.ca.pem')

def saveCRLList(crl_path, crl_pem_list):
  """
  Store given list of PEM-encoded Certificate Revocation Lists in given path.

  crl_path (str)
  May point to a directory a file, or nothing.
  If it does not exist, and this value contains an extension, a file is
  created, otherwise a directory is.
  If it is a file, all CRLs are written in it.
  If it is a folder, each CRL is stored in a separate file.

  crl_pem_list (list of bytes)
  """
  _savePEMList(
    crl_path,
    crl_pem_list,
    lambda x: x509.load_pem_x509_crl(x, _cryptography_backend),
    '.crl.pem',
  )

def _savePEMList(path, pem_list, pem_loader, extension):
  if os.path.exists(path):
    if os.path.isfile(path):
      savePEMList = _savePEMListToFile
    elif os.path.isdir(path):
      savePEMList = _savePEMListToDirectory
    else:
      raise TypeError('%s exist and is neither a directory nor a file' % (
        path,
      ))
  else:
    savePEMList = (
      _savePEMListToFile
      if os.path.splitext(path)[1] else
      _savePEMListToDirectory
    )
  savePEMList(path, pem_list, pem_loader, extension)

def _savePEMListToFile(file_path, pem_list, pem_loader, extension):
  _ = pem_loader # Silence pylint
  _ = extension # Silence pylint
  with open(file_path, 'wb') as pem_file:
    for pem_chunk in pem_list:
      pem_file.write(pem_chunk)

def _savePEMListToDirectory(dir_path, pem_list, pem_loader, extension):
  if not os.path.exists(dir_path):
    os.mkdir(dir_path)
  pem_dict = {
    hexlify(
      pem_loader(x).extensions.get_extension_for_class(
        x509.AuthorityKeyIdentifier,
      ).value.key_identifier,
    ).decode('ascii') + extension: x
    for x in pem_list
  }
  for filename in os.listdir(dir_path):
    filepath = os.path.join(dir_path, filename)
    if not filepath.endswith(extension) or not os.path.isfile(filepath):
      # Not a managed file name and not a symlink to a file, ignore
      continue
    if not os.path.islink(filepath) and filename in pem_dict:
      try:
        # pylint: disable=unbalanced-tuple-unpacking
        file_pem_item, = _getPEMTypeDict(filepath).values()
        # pylint: enable=unbalanced-tuple-unpacking
      # pylint: disable=broad-except
      except Exception:
      # pylint: enable=broad-except
        # File contains multiple PEM items: overwrite
        pass
      else:
        if file_pem_item == pem_dict[filename]:
          # Already consistent, do not edit.
          del pem_dict[filename]
    else:
      # Unknown file (ex: expired certificate), or a symlink to a file: delete
      os.unlink(filepath)
  for filename, pem_item in pem_dict.items():
    filepath = os.path.join(dir_path, filename)
    with open(filepath, 'wb') as pem_file:
      pem_file.write(pem_item)

def getCert(crt_path):
  """
  Return a certificate from a file which may also contain a key.
  Raises if there is more or less than one certificate.
  """
  type_dict = _getPEMTypeDict(crt_path)
  crt, = type_dict.get(pem.Certificate)
  return crt.as_bytes()

def getLeafCertificate(crt_path):
  """
  Return a regular (non-CA) certificate from a file which may contain a CA
  certificate and a key.
  Raises if there is more or less than one regular certificate.
  """
  type_dict = _getPEMTypeDict(crt_path)
  result_list = []
  for crt in type_dict.get(pem.Certificate, ()):
    crt_bytes = crt.as_bytes()
    if not x509.load_pem_x509_certificate(
      crt_bytes,
      _cryptography_backend,
    ).extensions.get_extension_for_class(
      x509.BasicConstraints,
    ).value.ca:
      result_list.append(crt_bytes)
  result, = result_list # pylint: disable=unbalanced-tuple-unpacking
  return result

def hasOneCert(crt_path):
  """
  Returns whether crt_path contains a certificate.

  False if there is no file at crt_path.
  Raises if there is more than one certificate.
  Ignores other types.
  """
  if os.path.exists(crt_path):
    crt_list = _getPEMTypeDict(crt_path).get(pem.Certificate, [])
    if crt_list:
      _, = crt_list
      return True
  return False

def getCertRequest(csr_path):
  """
  Return a certificate request from a file.
  Raises if there is more or less than one certificate request, or anything
  else.
  """
  type_dict = _getPEMTypeDict(csr_path)
  csr, = type_dict.pop(pem.CertificateRequest)
  if type_dict:
    raise ValueError('%s contains more than just a csr' % (csr_path, ))
  return csr.as_bytes()

def getKey(key_path):
  """
  Return a key from a file.
  Raises if there is more or less than one key, or anything else.
  """
  type_dict = _getPEMTypeDict(key_path)
  key, = type_dict.pop(pem.Key)
  if type_dict:
    raise ValueError('%s contains more than just a key' % (key_path, ))
  return key.as_bytes()

def getKeyPair(crt_path, key_path=None):
  """
  Return a certificate and a key from a pair of file.
  If crt_path contains both a cert and a key, key_path is ignored.
  Raises if there is more than one certificate or more than one key.
  Raises if key and cert do not match.
  """
  type_dict = _getPEMTypeDict(crt_path)
  if pem.Key not in type_dict and key_path:
    _getPEMTypeDict(key_path, type_dict)
  else:
    key_path = None
  key, = type_dict[pem.Key]
  crt, = type_dict[pem.Certificate]
  key = key.as_bytes()
  crt = crt.as_bytes()
  validateCertAndKey(crt, key)
  return crt, key, key_path

def validateCertAndKey(cert_pem, key_pem):
  """
  Verify certificate and key match.

  Raises if it is not the case.
  """
  if x509.load_pem_x509_certificate(
    cert_pem,
    _cryptography_backend,
  ).public_key().public_numbers() != load_privatekey(
    key_pem,
  ).public_key().public_numbers():
    raise ValueError('Mismatch between private key and certificate')

def _verifyCertificateChain(cert, trusted_cert_list, crl_list):
  """
  Verifies whether certificate has been signed by any of the trusted
  certificates, is not revoked and is whithin its validity period.

  Raises CertificateVerificationError if validation fails.
  """
  # Note: this function (validating a certificate without an SSL connection)
  # does not seem to have many equivalents at all in python. OpenSSL module
  # seems to be a rare implementation of it, so we keep using this module.
  # BUT it MUST NOT be used anywhere outside this function (hence the
  # bad-style local import). Use "cryptography".
  # Also, older pylint (last version suppoting 2.7 ?) does not support
  # import-outside-toplevel but does not detect anything wrong here.
  # pylint: disable=import-outside-toplevel
  from OpenSSL import crypto
  # pylint: enable=import-outside-toplevel
  store = crypto.X509Store()
  assert trusted_cert_list
  for trusted_cert in trusted_cert_list:
    store.add_cert(crypto.X509.from_cryptography(trusted_cert))
  if crl_list:
    if hasattr(crypto, 'CRL'): # pragma: no cover
      # BBB: pyOpenSSL < 24.3.0
      crl_list = [crypto.CRL.from_cryptography(x) for x in crl_list]
    for crl in crl_list:
      store.add_crl(crl)
    store.set_flags(crypto.X509StoreFlags.CRL_CHECK)
  try:
    crypto.X509StoreContext(
      store,
      crypto.X509.from_cryptography(cert),
    ).verify_certificate()
  except (
    crypto.X509StoreContextError,
    crypto.Error,
  ) as e:
    raise CertificateVerificationError(
      'Certificate verification error: %s' % str(e),
    )

def wrap(payload, key, digest):
  """
  Sign payload (which gets json-serialised) with key, using given digest.
  """
  payload = toBytes(json.dumps(payload), 'utf-8')
  hash_class = getattr(hashes, digest.upper())
  return {
    'payload': toUnicode(payload),
    'digest': digest,
    # For some reason, python3 thinks that a b2a method should return bytes.
    'signature': toUnicode(b2a_base64(key.sign(
      payload + toBytes(digest) + b' ',
      padding.PSS(
        mgf=padding.MGF1(hash_class()),
        salt_length=padding.PSS.MAX_LENGTH,
      ),
      hash_class(),
    ))),
  }

def nullWrap(payload):
  """
  Wrap without signature. To only be used (and accepted) when user is
  authenticated (and hence using a secure channel, HTTPS).
  """
  return {
    'payload': json.dumps(payload),
    'digest': None,
  }

def unwrap(wrapped, getCertificate, digest_list):
  """
  Check payload signature and return it.

  Raises cryptography.exceptions.InvalidSignature if signature does not match
  payload or if transmitted digest is not an acceptable one.

  Note: does *not* verify received certificate itself (validity, issuer, ...).
  """
  # Check whether given digest is allowed
  digest = wrapped['digest']
  if digest not in digest_list:
    raise cryptography.exceptions.UnsupportedAlgorithm(
      '%r is not in allowed digest list %r' % (digest, digest_list),
    )
  hash_class = getattr(hashes, digest.upper())
  try:
    payload = json.loads(wrapped['payload'])
  except ValueError:
    raise NotJSON
  x509.load_pem_x509_certificate(
    toBytes(getCertificate(payload)),
    _cryptography_backend,
  ).public_key().verify(
    a2b_base64(toBytes(wrapped['signature'])),
    toBytes(wrapped['payload'], 'utf-8') + toBytes(digest) + b' ',
    padding.PSS(
      mgf=padding.MGF1(hash_class()),
      salt_length=padding.PSS.MAX_LENGTH,
    ),
    hash_class(),
  )
  return payload

def nullUnwrap(wrapped):
  """
  Un-wrapp unsigned content. To onl be used on content received from
  an authenticated user (and hence over a secure channel, HTTPS).
  """
  assert wrapped['digest'] is None
  try:
    return json.loads(wrapped['payload'])
  except ValueError:
    raise NotJSON

def load_ca_certificate(data):
  """
  Load CA certificate from PEM-encoded data.

  Raises CertificateVerificationError if loaded certificate is not self-signed
  or is otherwise invalid.
  """
  crt = x509.load_pem_x509_certificate(data, _cryptography_backend)
  _verifyCertificateChain(crt, [crt], None)
  return crt

def iter_valid_ca_certificate_list(ca_pem_list):
  """
  Load multiple CA certificates from a list of PEM-encoded values.

  Yields the PEM-encoded value along with the loaded CA.

  Skips items failing to load.
  """
  for ca_pem in ca_pem_list:
    try:
      ca = load_ca_certificate(ca_pem)
    except CertificateVerificationError:
      continue
    else:
      yield (ca_pem, ca)

def load_valid_ca_certificate_list(ca_pem_list):
  """
  Load CA certificates from PEM-encoded data, skipping items which fail
  signature verification.

  Returns the list of loaded CA certificates.
  """
  return [
    ca
    for _, ca in iter_valid_ca_certificate_list(ca_pem_list)
  ]

def load_certificate(data, trusted_cert_list, crl_list):
  """
  Load a certificate from PEM-encoded data.

  Raises CertificateVerificationError if loaded certificate is not signed by
  any of trusted certificates, is revoked or is otherwise invalid.
  """
  crt = x509.load_pem_x509_certificate(data, _cryptography_backend)
  _verifyCertificateChain(crt, trusted_cert_list, crl_list)
  return crt

def dump_certificate(data):
  """
  Serialise a certificate as PEM-encoded data.
  """
  return data.public_bytes(encoding=serialization.Encoding.PEM)

def load_certificate_request(data):
  """
  Load a certificate request from PEM-encoded data.

  Raises cryptography.exceptions.InvalidSignature if certificate signature
  does not match embedded public key.
  """
  result = x509.load_pem_x509_csr(data, _cryptography_backend)
  if not result.is_signature_valid:
    raise cryptography.exceptions.InvalidSignature
  return result

def dump_certificate_request(data):
  """
  Serialise acertificate request as PEM-encoded data.
  """
  return data.public_bytes(encoding=serialization.Encoding.PEM)

def load_privatekey(data):
  """
  Load a private key from PEM-encoded data.
  """
  return serialization.load_pem_private_key(
    data,
    password=None,
    backend=_cryptography_backend,
  )

def dump_privatekey(data):
  """
  Serialise a private key as PEM-encoded data.
  """
  return data.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption(),
  )

def generatePrivateKey(key_len):
  """
  Generate a new private key of specified length.
  """
  return rsa.generate_private_key(
    public_exponent=65537,
    key_size=key_len,
    backend=_cryptography_backend,
  )

def load_crl(data, trusted_cert_list):
  """
  Load a certificate revocation list from PEM-encoded data.

  Raises cryptography.exceptions.InvalidSignature if the CRL signature does not
  match any trusted certificate.
  """
  crl = x509.load_pem_x509_crl(data, _cryptography_backend)
  for cert in trusted_cert_list:
    if crl.is_signature_valid(cert.public_key()):
      return crl
  raise cryptography.exceptions.InvalidSignature

def iter_valid_crl_list(crl_pem_list, trusted_cert_list):
  """
  Load multiple certificate revocation lists from a list of PEM-encoded values.

  Yields the PEM-encoded value along with the loaded CRL.

  Skips items failing to load.
  """
  for crl_pem in crl_pem_list:
    try:
      crl = load_crl(crl_pem, trusted_cert_list)
    except cryptography.exceptions.InvalidSignature:
      continue
    else:
      yield (crl_pem, crl)

def _getAuthorityKeyIdentifier(cert):
  return cert.extensions.get_extension_for_class(
    x509.AuthorityKeyIdentifier,
  ).value.key_identifier

if hasattr(x509.Certificate, 'not_valid_after_utc'): # pragma: no cover
  try:
    _UTC = datetime.timezone.utc
  except AttributeError:
    # BBB
    _ZERO_TIMEDELTA = datetime.timedelta(0)
    class _UTC(datetime.tzinfo):
      """UTC"""

      def utcoffset(self, dt):
        return _ZERO_TIMEDELTA

      def tzname(self, dt):
        return "UTC"

      def dst(self, dt):
        return _ZERO_TIMEDELTA
    _UTC = _UTC()

  def utcnow():
    """
    Get a datetime instance of the current time in UTC.
    """
    return datetime.datetime.now(_UTC)

  def getNotValidAfter(obj):
    """
    Return the not_valid_after date from given cyrptography object.
    """
    return obj.not_valid_after_utc

  def getNotValidBefore(obj):
    """
    Return the not_valid_before date from given cyrptography object.
    """
    return obj.not_valid_before_utc

  def getLastUpdate(obj):
    """
    Return the last_update date from given cyrptography object.
    """
    return obj.last_update_utc

  def getNextUpdate(obj):
    """
    Return the next_update date from given cyrptography object.
    """
    return obj.next_update_utc

  def getRevocationDate(obj):
    """
    Return the revocation_date from given cyrptography object.
    """
    return obj.revocation_date_utc
else: # pragma: no cover
  # BBB

  _UTC = None

  def utcnow():
    """
    Get a datetime instance of the current time in UTC.
    """
    return datetime.datetime.utcnow()

  def getNotValidAfter(obj):
    """
    Return the not_valid_after date from given cyrptography object.
    """
    return obj.not_valid_after

  def getNotValidBefore(obj):
    """
    Return the not_valid_before date from given cyrptography object.
    """
    return obj.not_valid_before

  def getLastUpdate(obj):
    """
    Return the last_update date from given cyrptography object.
    """
    return obj.last_update

  def getNextUpdate(obj):
    """
    Return the next_update date from given cyrptography object.
    """
    return obj.next_update

  def getRevocationDate(obj):
    """
    Return the revocation_date from given cyrptography object.
    """
    return obj.revocation_date

EPOCH = datetime.datetime(1970, 1, 1, tzinfo=_UTC)
def datetime2timestamp(value):
  """
  Convert given datetime into a unix timestamp.
  """
  return int((value - EPOCH).total_seconds())

def timestamp2datetime(value):
  """
  Convert given unix timestamp into a datetime.
  """
  return EPOCH + datetime.timedelta(seconds=value)

def timestamp2IMFfixdate(value):
  """
  Convert a timestamp into an IMF-fixdate string following RFC7231.
  """
  return email.utils.formatdate(
    value,
    localtime=False,
    usegmt=True,
  )

def IMFfixdate2timestamp(value):
  """
  Convert an IMF-fixdate string following RFC7231 into a timestamp.
  """
  result = email.utils.parsedate(value)
  if result is None:
    return None
  return calendar.timegm(result)

class SleepInterrupt(KeyboardInterrupt):
  """
  A sleep was interrupted by a KeyboardInterrupt
  """
  pass

def toUnicode(value, encoding='ascii'):
  """
  Convert value to unicode object, if it is not already.
  """
  # pylint: disable=possibly-used-before-assignment
  return value if isinstance(value, unicode) else value.decode(encoding)
  # pylint: enable=possibly-used-before-assignment

def toBytes(value, encoding='ascii'):
  """
  Convert value to bytes object, if it is not already.
  """
  return value if isinstance(value, bytes) else value.encode(encoding)

def toUnicodeWritableStream(writable_stream, encoding='ascii'):
  """
  Convert writable_stream into a writable stream accepting unicode.
  If writable_stream already accepts unicode, returns it.
  Otherwise, returns a writable stream accepting unicode, and sending it to
  writable_stream encoded with given encoding.
  """
  if (
    isinstance(writable_stream, codecs.StreamWriter) or
    getattr(writable_stream, 'encoding', None) is not None
  ):
    return writable_stream
  return codecs.getwriter(encoding)(writable_stream)

def interruptibleSleep(duration): # pragma: no cover
  """
  Like sleep, but raises SleepInterrupt when interrupted by KeyboardInterrupt
  """
  try:
    time.sleep(duration)
  except KeyboardInterrupt:
    raise SleepInterrupt

def until(deadline): # pragma: no cover
  """
  Call interruptibleSleep until deadline is reached.
  """
  try:
    while True:
      now = utcnow()
      remaining_time = (deadline - now).total_seconds()
      if remaining_time <= 0:
        break
      # Wake up half-way to the deadline, to re-evaluate the time left: the
      # computer may have been suspended, or had its time changed.
      # ...but do not sleep less than 10 minutes.
      # ...but do not sleep past the deadline.
      # Simulating a computer suspended 75% of the time (continuously, which is
      # a big approximation of the actual discrete nature of suspend periods)
      # shows this approach should lead to 5 wakeups for a deadline initially
      # 7 days away: first wakeup after 6.1 days, second 18 hours later, then
      # 2 hours, then 17 minutes and finally the few remaining seconds.
      interruptibleSleep(
        max(
          remaining_time / 2,
          min(
            remaining_time,
            600,
          ),
        ),
      )
  except KeyboardInterrupt:
    raise SleepInterrupt
  return now

def log_exception(error_file, exc_info, client_address):
  """
  Log an unhandled exception to error_file, using a somewhat apache-inspired
  format.
  """
  try:
    print(
      '[%s] [pid %s:tid %s] [client %s] %s %s%s' % (
        utcnow().isoformat(),
        os.getpid(),
        threading.current_thread().ident,
        client_address,
        exc_info[1],
        os.linesep,
        ''.join(traceback.format_exception(
          exc_info[0],
          exc_info[1],
          exc_info[2],
        )),
      ),
      end='', # format_exc has its own linesep
      file=error_file,
    )
  finally:
    exc_info = None
