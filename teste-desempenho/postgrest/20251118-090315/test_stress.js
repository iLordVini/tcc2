import http from 'k6/http';
import { check, group, sleep } from 'k6';
export const options = { "stages": [ { "duration": "2m", "target": 50 }, { "duration": "5m", "target": 50 }, { "duration": "1m", "target": 0 } ] };
const BASE_URL = 'http://localhost:3000';
const MIN_ID = 1;
const MAX_ID = 1000000;
export default function () {
  const rand = Math.random();
  const randomId = Math.floor(Math.random() * (MAX_ID - MIN_ID + 1)) + MIN_ID;
  if (rand < 0.80) {
    group('GET - Leitura', function () {
      const r = http.get(`${BASE_URL}/products?id=eq.${randomId}`);
      check(r, { 'GET status 200': (x) => x.status === 200 });
      sleep(0.2);
    });
  } else {
    group('POST - Criar', function () {
      const create = http.post(
        `${BASE_URL}/products`,
        JSON.stringify({ name: "Produto Teste PostgREST", price: 1 }),
        { headers: { 'Content-Type': 'application/json', 'Prefer': 'return=representation' } }
      );
      check(create, { 'POST 201': (r) => r.status === 201 });
      sleep(0.2);
    });
  }
}