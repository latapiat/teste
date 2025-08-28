import http from 'http';

// Cria um servidor HTTP simples
const server = http.createServer((req, res) => {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('Seja bem-vindo ao meu app Node.js no Vercel!');
});

const port = 3000;
server.listen(port, () => {
  console.log(`Servidor rodando na porta ${port}`);
});
