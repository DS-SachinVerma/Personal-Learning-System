from pathlib import Path
path = Path('src/components/Notes.jsx')
text = path.read_text(encoding='utf-8')
text = text.replace("import ReactMarkdown from 'react-markdown';\n", '')
text = text.replace('<ReactMarkdown className="markdown-preview">{newNote.content}</ReactMarkdown>', '<div className="markdown-preview" style={{ whiteSpace: \'pre-wrap\' }}>{newNote.content}</div>')
text = text.replace('<ReactMarkdown>{newNote.content || \'*Start writing your note...*\'}</ReactMarkdown>', '<div className="markdown-preview" style={{ whiteSpace: \'pre-wrap\' }}>{newNote.content || \'*Start writing your note...*\'}</div>')
path.write_text(text, encoding='utf-8')
print('updated')
