# Sprint 2 Verification (Counter-Orion)

## Scope covered
- Catalog-ready schema (`skins_catalog`, `user_skins`)
- Catalog seed pipeline (Covert + Extraordinary)
- Catalog API (`/catalog/skins`, `/catalog/skins/search`)
- Inventory API CRUD (`/skins`)
- Inventory UI (`/inventory`) + profile inventory snapshot (`/profile`)

## Automated API verification
Run from VM2:

```bash
python3 - <<'PY'
import json, urllib.request, urllib.error, time

BASE='http://localhost:8082'


def req(method, path, data=None, token=None):
    headers={}
    if data is not None:
        headers['Content-Type']='application/json'
    if token:
        headers['Authorization']=f'Bearer {token}'
    body=json.dumps(data).encode() if data is not None else None
    r=urllib.request.Request(BASE+path, data=body, headers=headers, method=method)
    with urllib.request.urlopen(r) as resp:
        return resp.status, json.loads(resp.read().decode())


def expect_http_error(method, path, code, data=None, token=None):
    headers={}
    if data is not None:
        headers['Content-Type']='application/json'
    if token:
        headers['Authorization']=f'Bearer {token}'
    body=json.dumps(data).encode() if data is not None else None
    r=urllib.request.Request(BASE+path, data=body, headers=headers, method=method)
    try:
        urllib.request.urlopen(r)
    except urllib.error.HTTPError as e:
        return e.code == code
    return False

uid=str(int(time.time()))
email_a=f's2a+{uid}@orion.local'
user_a=f's2a_{uid}'
email_b=f's2b+{uid}@orion.local'
user_b=f's2b_{uid}'
pw='test1234'

req('POST','/auth/register',{'email':email_a,'username':user_a,'password':pw})
req('POST','/auth/register',{'email':email_b,'username':user_b,'password':pw})
_,login_a=req('POST','/auth/login',{'email':email_a,'password':pw})
_,login_b=req('POST','/auth/login',{'email':email_b,'password':pw})

TA=login_a['access_token']
TB=login_b['access_token']

_,catalog=req('GET','/catalog/skins?page=1&page_size=1',token=TA)
catalog_id=catalog['items'][0]['id']

_,created=req('POST','/skins',{
    'catalog_skin_id': catalog_id,
    'wear':'Factory New',
    'stattrak': True,
    'quantity': 1,
    'note':'owner-a',
    'buy_price_eur': 123.45
}, token=TA)
item_id=created['id']

_,list_a=req('GET','/skins',token=TA)
_,list_b=req('GET','/skins',token=TB)

ownership_read_ok = list_a['total'] == 1 and list_b['total'] == 0
ownership_update_blocked = expect_http_error('PUT', f'/skins/{item_id}', 404, {'quantity':3}, token=TB)
ownership_delete_blocked = expect_http_error('DELETE', f'/skins/{item_id}', 404, token=TB)

invalid_catalog = expect_http_error('POST', '/skins', 404, {'catalog_skin_id': 999999}, token=TA)
invalid_qty = expect_http_error('POST', '/skins', 400, {'catalog_skin_id': catalog_id, 'quantity': 0}, token=TA)
invalid_price = expect_http_error('POST', '/skins', 400, {'catalog_skin_id': catalog_id, 'buy_price_eur': -1}, token=TA)
unauthorized_skins = expect_http_error('GET', '/skins', 401)

print(json.dumps({
  'ownership_read_ok': ownership_read_ok,
  'ownership_update_blocked': ownership_update_blocked,
  'ownership_delete_blocked': ownership_delete_blocked,
  'invalid_catalog': invalid_catalog,
  'invalid_qty': invalid_qty,
  'invalid_price': invalid_price,
  'unauthorized_skins': unauthorized_skins
}, indent=2))
PY
```

Expected: all checks should be `true`.
