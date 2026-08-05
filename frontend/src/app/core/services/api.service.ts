import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class ApiService {
  // URL relativa — nginx proxea /api/ → backend en Docker
  // Dev local: usar proxy.conf.json con ng serve --proxy-config proxy.conf.json
  protected baseUrl = '/api/v1';

  constructor(protected http: HttpClient) {}
}
