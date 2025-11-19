import http from 'k6/http';
import { check, group, sleep } from 'k6';
export const options = { "stages": [ { "duration": "2m", "target": 25 }, { "duration": "7m", "target": 25 }, { "duration": "2m", "target": 0 } ] };
const BASE_URL = 'http://localhost:3001/marketplace/public';
const MIN_ID = 1;
const MAX_ID = 1000000;
export default function () {
  const rand = Math.random();
  const randomId = Math.floor(Math.random() * (MAX_ID - MIN_ID + 1)) + MIN_ID;
  if (rand < 0.80) {
    group('GET - Leitura', function () {
      const r = http.get(`${BASE_URL}/products?id=${randomId}`);
      check(r, { 'GET status 200': (x) => x.status === 200 });
      sleep(0.2);
    });
  } else {
    group('POST - Criar', function () {
      const create = http.post(
        `${BASE_URL}/products`,
        JSON.stringify({ name: "Produto Teste pREST", price: 1 }),
        { headers: { 'Content-Type': 'application/json' } }
      );
      check(create, { 'POST 2xx': (r) => r.status === 201 || r.status === 200 });
      sleep(0.2);
    });
  }
}