import json
import urllib.request

payload = {
  "tipo_sacramento": 1,
  "fecha_sacramento": "2025-11-27",
  "institucion": "Parroquia Test",
  "ministro": "P. Test",
  "person_name": "Prueba Usuario",
  "person_birthdate": "1990-01-01",
  "father_name": "Padre Prueba",
  "mother_name": "Madre Prueba",
  "godparent_1_name": "Padrino Prueba",
  "libro": "1",
  "folio": "1",
  "numero_acta": "123",
  "observaciones": "Creado por smoke test"
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request('http://localhost:8002/api/v1/sacramentos/', data=data, headers={'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        print('STATUS', resp.status)
        print(resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('HTTP ERROR', e.code)
    try:
        body = e.read().decode('utf-8')
        print(body)
    except Exception:
        pass
except Exception as e:
    print('ERROR', str(e))
