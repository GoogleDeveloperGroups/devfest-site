# -*- coding: utf-8 -*-
from webob import multidict

def from_fieldstorage(cls, fs):
  """Create a dict from a cgi.FieldStorage instance.

  See this for more details:
  http://code.google.com/p/googleappengine/issues/detail?id=2749
  """
  import base64
  import quopri

  obj = cls()
  if fs.list:
    # fs.list can be None when there's nothing to parse
    for field in fs.list:
      if field.filename:
        obj.add(field.name, field)
      else:

        # first, set a common charset to utf-8.
        common_charset = 'utf-8'

        # second, check Content-Transfer-Encoding and decode
        # the value appropriately
        field_value = field.value
        transfer_encoding = field.headers.get(
          'Content-Transfer-Encoding', None)

        if transfer_encoding == 'base64':
          field_value = base64.b64decode(field_value)

        if transfer_encoding == 'quoted-printable':
          field_value = quopri.decodestring(field_value)

        if field.type_options.has_key('charset') and field.type_options['charset'] != common_charset:
          # decode with a charset specified in each
          # multipart, and then encode it again with a
          # charset specified in top level FieldStorage
          field_value = field_value.decode(
            field.type_options['charset']).encode(common_charset
          )

        # TODO: Should we take care of field.name here?
        obj.add(field.name, field_value)

  return obj

multidict.MultiDict.from_fieldstorage = classmethod(from_fieldstorage)

