// server.js
const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const { createProxyServer } = require('http-proxy');
require('dotenv').config();

const ASSEMBLYAI_API_KEY = process.env.ASSEMBLYAI_API_KEY;
const ASSEMBLYAI_WS_URL = 'wss://api.assemblyai.com/v2/realtime/universal';

if (!ASSEMBLYAI_API_KEY) {
  console.error('Missing ASSEMBLYAI_API_KEY in environment');
  process.exit(1);
}

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server, path: '/realtime' });

wss.on('connection', (clientWs, req) => {
  // Connect to AssemblyAI with Authorization header
  const aaiWs = new WebSocket(ASSEMBLYAI_WS_URL, {
    headers: { Authorization: ASSEMBLYAI_API_KEY }
  });

  // Forward messages from client to AssemblyAI
  clientWs.on('message', (msg) => {
    if (aaiWs.readyState === WebSocket.OPEN) aaiWs.send(msg);
  });

  // Forward messages from AssemblyAI to client
  aaiWs.on('message', (msg) => {
    clientWs.send(msg);
  });

  // Log and forward close/error events
  aaiWs.on('close', (code, reason) => clientWs.close(code, reason));
  aaiWs.on('error', (err) => {
    console.error('AssemblyAI WS error:', err);
    clientWs.close(1011, 'AssemblyAI error');
  });

  clientWs.on('close', () => aaiWs.close());
  clientWs.on('error', (err) => {
    console.error('Client WS error:', err);
    aaiWs.close(1011, 'Client error');
  });
});

app.use(express.static('templates')); // Serve frontend from /templates

const PORT = process.env.PORT || 5001;
server.listen(PORT, () => {
  console.log(`Proxy server running on http://localhost:${PORT}`);
});