'use client';

/* eslint-disable @next/next/no-img-element */
import React, { MutableRefObject, useEffect, useState } from 'react';
import { Message } from './ChatWindow';
import { cn } from '@/lib/utils';
import {
  BookCopy,
  Disc3,
  Layers3,
  Plus,
} from 'lucide-react';
import Markdown, { MarkdownToJSX } from 'markdown-to-jsx';
import Copy from './MessageActions/Copy';
import Rewrite from './MessageActions/Rewrite';
import MessageSources from './MessageSources';
import ThinkBox from './ThinkBox';

const ThinkTagProcessor = ({ children }: { children: React.ReactNode }) => {
  return <ThinkBox content={children as string} />;
};

const MessageBox = ({
  message,
  messageIndex,
  history,
  loading,
  dividerRef,
  isLast,
  rewrite,
  sendMessage,
}: {
  message: Message;
  messageIndex: number;
  history: Message[];
  loading: boolean;
  dividerRef?: MutableRefObject<HTMLDivElement | null>;
  isLast: boolean;
  rewrite: (messageId: string) => void;
  sendMessage: (message: string) => void;
}) => {
  const [parsedMessage, setParsedMessage] = useState(message.content);

  useEffect(() => {
    const regex = /\[(\d+)\]/g;
    let processedMessage = message.content;

    if (message.role === 'assistant' && message.content.includes('<think>')) {
      const openThinkTag = processedMessage.match(/<think>/g)?.length || 0;
      const closeThinkTag = processedMessage.match(/<\/think>/g)?.length || 0;

      if (openThinkTag > closeThinkTag) {
        processedMessage += '</think> <a> </a>'; // The extra <a> </a> is to prevent the the think component from looking bad
      }
    }

    if (
      message.role === 'assistant' &&
      message?.sources &&
      message.sources.length > 0
    ) {
      setParsedMessage(
        processedMessage.replace(
          regex,
          (_, number) =>
            `<a href="${
              message.sources?.[number - 1]?.metadata?.url
            }" target="_blank" className="bg-light-secondary dark:bg-dark-secondary px-1 rounded ml-1 no-underline text-xs text-black/70 dark:text-white/70 relative">${number}</a>`,
        ),
      );
      return;
    }

    setParsedMessage(processedMessage);
  }, [message.content, message.sources, message.role]);

  const markdownOverrides: MarkdownToJSX.Options = {
    overrides: {
      think: {
        component: ThinkTagProcessor,
      },
    },
  };

  return (
    <div>
      {message.role === 'user' && (
        <div
          className={cn(
            'w-full',
            messageIndex === 0 ? 'pt-16' : 'pt-8',
            'break-words',
          )}
        >
          <h2 className="text-black dark:text-white font-medium text-3xl lg:w-9/12">
            {message.content}
          </h2>
        </div>
      )}

      {message.role === 'assistant' && (
        <div className="flex flex-col space-y-9">
          <div
            ref={dividerRef}
            className="flex flex-col space-y-6 w-full"
          >
            {message.sources && message.sources.length > 0 && (
              <div className="flex flex-col space-y-2">
                <div className="flex flex-row items-center space-x-2">
                  <BookCopy className="text-black dark:text-white" size={20} />
                  <h3 className="text-black dark:text-white font-medium text-xl">
                    Sources
                  </h3>
                </div>
                <MessageSources sources={message.sources} />
              </div>
            )}
            <div className="flex flex-col space-y-2">
              <div className="flex flex-row items-center space-x-2">
                <Disc3
                  className={cn(
                    'text-black dark:text-white',
                    isLast && loading ? 'animate-spin' : 'animate-none',
                  )}
                  size={20}
                />
                <h3 className="text-black dark:text-white font-medium text-xl">
                  Answer
                </h3>
              </div>

              <Markdown
                className={cn(
                  'prose prose-h1:mb-3 prose-h2:mb-2 prose-h2:mt-6 prose-h2:font-[800] prose-h3:mt-4 prose-h3:mb-1.5 prose-h3:font-[600] dark:prose-invert prose-p:leading-relaxed prose-pre:p-0 font-[400]',
                  'max-w-none break-words text-black dark:text-white',
                )}
                options={markdownOverrides}
              >
                {parsedMessage}
              </Markdown>
              {loading && isLast ? null : (
                <div className="flex flex-row items-center justify-between w-full text-black dark:text-white py-4 -mx-2">
                  <div className="flex flex-row items-center space-x-1">
                    <Rewrite rewrite={rewrite} messageId={message.messageId} />
                  </div>
                  <div className="flex flex-row items-center space-x-1">
                    <Copy initialMessage={message.content} message={message} />
                  </div>
                </div>
                )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MessageBox;
