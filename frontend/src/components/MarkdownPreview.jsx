import { Component, forwardRef, Children, createElement } from 'react';
import ReactMarkdown from 'react-markdown';

class PreviewErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidUpdate(prevProps) {
    if (prevProps.content !== this.props.content && this.state.hasError) {
      this.setState({ hasError: false });
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="markdown-preview error">
          <p>Unable to render preview. Please check your markdown content.</p>
        </div>
      );
    }

    return this.props.children;
  }
}

const getHeadingId = (children) => {
  const text = Children.toArray(children)
    .filter((child) => typeof child === 'string')
    .join('');
  return text.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, '');
};

const Heading = ({ level, children, ...rest }) => {
  const id = getHeadingId(children);
  const Tag = `h${level}`;
  return createElement(Tag, { id, ...rest }, children);
};

const MarkdownPreview = forwardRef(({ content }, ref) => (
  <PreviewErrorBoundary content={content}>
    <div className="markdown-preview" ref={ref}>
      <ReactMarkdown
        components={{
          h1: Heading,
          h2: Heading,
          h3: Heading,
          h4: Heading,
          h5: Heading,
          h6: Heading,
        }}
      >
        {content || '*Nothing written yet.*'}
      </ReactMarkdown>
    </div>
  </PreviewErrorBoundary>
));

export default MarkdownPreview;
