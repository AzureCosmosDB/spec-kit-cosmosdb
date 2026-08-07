'use strict';

const fs = require('fs');
const path = require('path');

const source = path.resolve(__dirname, '../../prompts');
const destination = path.resolve(__dirname, '../templates/prompts');

fs.rmSync(destination, { recursive: true, force: true });
fs.mkdirSync(path.dirname(destination), { recursive: true });
fs.cpSync(source, destination, { recursive: true });