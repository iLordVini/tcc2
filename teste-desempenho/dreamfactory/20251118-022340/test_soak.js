import http from 'k6/http';
import { check, group, sleep } from 'k6';
export const options = { "stages": [ { "duration": "2m", "target": 15 }, { "duration": "15m", "target": 15 }, { "duration": "3m", "target": 0 } ] };
const BASE_URL = 'http://localhost:3002/api/v2/public/_table';
const API_KEY = '46624cdc2e657389f229066bf9092e8accea917c0c426fe2b8e0ac2edf80b0ac';
const MIN_ID = 1;
const MAX_ID = 1000000;
export default function () {
  const rand = Math.random();
  const randomId = Math.floor(Math.random() * (MAX_ID - MIN_ID + 1)) + MIN_ID;
  if (rand < 0.80) {
    group('GET - Leitura', function () {
      const r = http.get(
        `${BASE_URL}/products/${randomId}`,
        { headers: { 'X-DreamFactory-Api-Key': API_KEY } }
      );
      check(r, { 'GET status 200': (x) => x.status === 200 });
      sleep(0.2);
    });
  } else {
    group('POST - Criar', function () {
      const create = http.post(
        `${BASE_URL}/products`,
        JSON.stringify({ resource: [{ name: "Produto Teste DreamFactory", price: 1 }] }),
        { headers: { 'X-DreamFactory-Api-Key': API_KEY, 'Content-Type': 'application/json' } }
      );
      check(create, { 'POST 2xx': (r) => r.status === 201 || r.status === 200 });
      sleep(0.2);
    });
  }
}