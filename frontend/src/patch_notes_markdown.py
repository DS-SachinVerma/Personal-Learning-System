from pathlib import Path
path = Path(__file__).with_name('components').joinpath('Notes.jsx')
text = path.read_text(encoding='utf-8')
text = text.replace(
    '<div className="markdown-preview">{newNote.content}</div>',
    '<div className="markdown-preview"><ReactMarkdown>{newNote.content or "*Start writing your note...*"}</ReactMarkdown></div>'
)
text = text.replace(
    '<div className="markdown-preview" style={{ whiteSpace: \'pre-wrap\' }}>{newNote.content || \'*Start writing your note...*\'}</div>',
    '<div className="markdown-preview"><ReactMarkdown>{newNote.content or "*Start writing your note...*"}</ReactMarkdown></div>'
)
path.write_text(text, encoding='utf-8')
print('patched')
