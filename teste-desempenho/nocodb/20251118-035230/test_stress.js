import http from 'k6/http';
import { check, group, sleep } from 'k6';
export const options = { "stages": [ { "duration": "2m", "target": 50 }, { "duration": "5m", "target": 50 }, { "duration": "1m", "target": 0 } ] };
const BASE_URL = 'http://localhost:8080/api/v2';
const TOKEN = 'wYf774fyGotOY30u0yHQnzb7p6VYsT-t5UCRE97W';
const TABLE_PRODUCTS = 'mnjffmzxhy9jt2t';
const MIN_ID = 1;
const MAX_ID = 1000000;
export default function () {
  const headers = { 'xc-token': TOKEN, 'Content-Type': 'application/json' };
  const randomId = Math.floor(Math.random() * (MAX_ID - MIN_ID + 1)) + MIN_ID;
  group('GET - Leitura', function () {
    const r = http.get(`${BASE_URL}/tables/${TABLE_PRODUCTS}/records/${randomId}`, { headers });
    check(r, { 'GET status 200': (x) => x.status === 200 });
    sleep(0.2);
  });
}