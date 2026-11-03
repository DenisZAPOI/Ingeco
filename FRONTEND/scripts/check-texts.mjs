// Fails when an interface text is written in the code instead of src/i18n/
// (cahier des charges, §6; docs/adr/013). Reads the code with the TypeScript
// parser, so comments are ignored. What counts as a text:
//   - text between JSX tags (<p>Bonjour</p>);
//   - a JSX attribute string with a letter and a space (label="Votre numéro");
//   - any string with a French letter or sign (é, à, «, », ’, …).
// A line that must keep such a string (a format code, a test) ends with the
// comment `// texte-autorisé`.
// Usage: npm run lint:texts

import fs from 'node:fs';
import path from 'node:path';
import ts from 'typescript';

const ROOT = path.resolve(import.meta.dirname, '../src');
const SKIPPED_DIRS = [path.join(ROOT, 'i18n'), path.join(ROOT, 'types')];
const FRENCH_SIGNS = /[À-ÖØ-öø-ÿŒœ«»’…]/;
const LETTER = /\p{L}/u;
const SPACE = /\s/;
// Attributes whose value is code, never shown to the user.
const CODE_ATTRIBUTES = new Set(['className', 'd', 'viewBox', 'points', 'transform', 'href', 'to', 'rel', 'target']);
const ALLOWED_MARK = 'texte-autorisé';

function* sourceFiles(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (!SKIPPED_DIRS.includes(full)) yield* sourceFiles(full);
    } else if (/\.tsx?$/.test(entry.name) && !/\.test\.tsx?$/.test(entry.name)) {
      yield full;
    }
  }
}

function problems(file) {
  const code = fs.readFileSync(file, 'utf8');
  const lines = code.split('\n');
  const source = ts.createSourceFile(file, code, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
  const found = [];

  function report(node, text) {
    const line = source.getLineAndCharacterOfPosition(node.getStart(source)).line;
    if (!lines[line].includes(ALLOWED_MARK)) {
      found.push(`${path.relative(process.cwd(), file)}:${line + 1}  ${text.trim().slice(0, 70)}`);
    }
  }

  function visit(node) {
    if (ts.isJsxText(node)) {
      if (LETTER.test(node.text)) report(node, node.text);
    } else if (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node) || ts.isTemplateLiteralToken(node)) {
      const parent = node.parent;
      const isAttribute = parent && ts.isJsxAttribute(parent);
      if (isAttribute) {
        const name = parent.name.getText(source);
        if (!CODE_ATTRIBUTES.has(name) && LETTER.test(node.text) && SPACE.test(node.text)) report(node, node.text);
      } else if (FRENCH_SIGNS.test(node.text) && !ts.isImportDeclaration(parent)) {
        report(node, node.text);
      }
    }
    ts.forEachChild(node, visit);
  }

  visit(source);
  return found;
}

const all = [...sourceFiles(ROOT)].flatMap(problems);
if (all.length > 0) {
  console.error(`${all.length} texte(s) écrit(s) dans le code au lieu de src/i18n/ :\n`);
  console.error(all.join('\n'));
  process.exit(1);
}
console.log('Aucun texte en dur hors de src/i18n/.');
