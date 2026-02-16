import React from 'react';
import './Message.css';

const Message = ({ message, isUser, metadata }) => {
  return (
    <div className={`message-container ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-bubble">
        <div className="message-content">{message}</div>
        {metadata && !isUser && (
          <div className="message-metadata">
            <div className="metadata-item">
              <span className="metadata-label">Route:</span>
              <span className={`metadata-badge ${metadata.route_category}`}>
                {metadata.route_category}
              </span>
            </div>
            <div className="metadata-item">
              <span className="metadata-label">Model:</span>
              <span className="metadata-value">{metadata.model_used}</span>
            </div>
            <div className="metadata-item">
              <span className="metadata-label">Method:</span>
              <span className="metadata-value">{metadata.routing_method}</span>
            </div>
            {metadata.calculator_used && (
              <div className="metadata-item calculation">
                <span className="metadata-label">🧮 Calculation:</span>
                <span className="metadata-value">
                  {metadata.calculation} = {metadata.calculation_result}
                </span>
              </div>
            )}
            {metadata.contexts_used && (
              <div className="metadata-item">
                <span className="metadata-label">📄 Contexts:</span>
                <span className="metadata-value">{metadata.contexts_used}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Message;
