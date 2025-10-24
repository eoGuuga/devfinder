---
title: DevFinder Pro API
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
pinned: false
---





# DevFinder 🚀

![Prévia do DevFinder](./assets/images/devfinder-preview.png)

## 📖 Sobre

DevFinder é uma aplicação web que permite aos usuários buscar perfis de desenvolvedores no GitHub e visualizar suas informações públicas e uma lista de seus principais repositórios. Este projeto foi desenvolvido como um desafio de front-end para demonstrar habilidades em consumo de APIs, manipulação do DOM e design responsivo.

**[➡️ Veja o projeto ao vivo!](link-para-o-seu-deploy-no-netlify-ou-vercel)**

---

## ✨ Funcionalidades

- **Busca de Usuários:** Pesquise por qualquer usuário do GitHub.
- **Visualização de Perfil:** Exibe informações detalhadas como avatar, nome, bio, número de seguidores e repositórios.
- **Listagem de Repositórios:** Mostra os repositórios públicos do usuário, ordenados por número de estrelas para destacar os mais relevantes.
- **Link Direto:** Cada repositório listado possui um link direto para o GitHub.
- **Tratamento de Erros:** Exibe uma mensagem amigável caso o usuário não seja encontrado.
- **Design Responsivo:** Interface totalmente adaptável para desktops, tablets e celulares.

---

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias e conceitos:

- **HTML5:** Estruturação semântica e acessível.
- **CSS3:** Estilização moderna, Flexbox/Grid para layout e Variáveis CSS para um mini Design System.
- **JavaScript (Vanilla JS):** Lógica da aplicação, manipulação do DOM e comunicação com a API.
- **Git e GitHub:** Versionamento e hospedagem do código.
- **API REST:** Consumo de dados através da [API oficial do GitHub](https://docs.github.com/pt/rest).
- **Conceitos de UX/UI:** Foco em uma experiência de usuário limpa e um design intuitivo.

---

## 🧠 Desafios e Aprendizados

Durante o desenvolvimento do DevFinder, o principal desafio foi gerenciar os diferentes estados da aplicação (inicial, carregando, sucesso, erro) de forma limpa e eficiente. A implementação da lógica assíncrona com `async/await` para consumir a API do GitHub foi um grande aprendizado, especialmente no que diz respeito ao tratamento de respostas e erros.

Este projeto solidificou meus conhecimentos em:

- Comunicação assíncrona com `fetch`.
- Manipulação dinâmica do DOM para renderizar dados.
- Organização de código JavaScript em módulos/funções com responsabilidades únicas.
- A importância de um design "mobile-first" para garantir a usabilidade em qualquer dispositivo.

---

## 🚀 Como Executar o Projeto

Para executar este projeto localmente, siga os passos abaixo:

1. Clone o repositório:
   ```bash
   git clone [https://github.com/eoGuuga/devfinder.git](https://github.com/eoGuuga/devfinder.git)
