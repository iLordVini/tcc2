import http from 'k6/http';
import { check, group, sleep } from 'k6';
export const options = { "stages": [ { "duration": "2m", "target": 50 }, { "duration": "5m", "target": 50 }, { "duration": "1m", "target": 0 } ] };
const BASE_URL = 'http://localhost:3002/api/v2/public/_table';
const API_KEY = '46624cdc2e657389f229066bf9092e8accea917c0c426fe2b8e0ac2edf80b0ac';
const MIN_ID = 1;
const MAX_ID = 1000000;
export default function () {
  const randomId = Math.floor(Math.random() * (MAX_ID - MIN_ID + 1)) + MIN_ID;
  group('GET - Leitura', function () {
    const r = http.get(`${BASE_URL}/products/${randomId}`, {
      headers: { 'X-DreamFactory-Api-Key': API_KEY }
    });
    check(r, { 'GET status 200': (x) => x.status === 200 });
    sleep(0.2);
  });
}