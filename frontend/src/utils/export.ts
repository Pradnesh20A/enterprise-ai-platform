import type { Citation } from '../api/client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
}

export const exportConversationToMarkdown = (messages: Message[]) => {
  let markdown = `# Enterprise AI Conversation Export\n\n`;
  markdown += `**Date:** ${new Date().toLocaleString()}\n\n---\n\n`;

  messages.forEach(msg => {
    const role = msg.role === 'user' ? '👤 **User**' : '🤖 **Assistant**';
    markdown += `### ${role}\n\n`;
    markdown += `${msg.content}\n\n`;
    
    if (msg.citations && msg.citations.length > 0) {
      markdown += `*Sources:*\n`;
      msg.citations.forEach(cit => {
        markdown += `- **${cit.filename}**: "${cit.snippet.replace(/\n/g, ' ')}"\n`;
      });
      markdown += `\n`;
    }
    
    markdown += `---\n\n`;
  });

  const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = `Enterprise_AI_Chat_${new Date().toISOString().split('T')[0]}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
