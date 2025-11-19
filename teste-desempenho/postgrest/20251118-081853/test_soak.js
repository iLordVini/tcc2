import http from 'k6/http';
import { check, group, sleep } from 'k6';
export const options = { "stages": [ { "duration": "2m", "target": 15 }, { "duration": "15m", "target": 15 }, { "duration": "3m", "target": 0 } ] };
const BASE_URL = 'http://localhost:3000';
const MIN_ID = 1;
const MAX_ID = 1000000;
export default function () {
  const randomId = Math.floor(Math.random() * (MAX_ID - MIN_ID + 1)) + MIN_ID;
  group('GET - Leitura', function () {
    const r = http.get(`${BASE_URL}/products?id=eq.${randomId}`);
    check(r, { 'GET status 200': (x) => x.status === 200 });
    sleep(0.2);
  });
}