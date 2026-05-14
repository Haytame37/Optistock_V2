'use client';

import React, { useState, useRef, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { chatService, ChatMessage } from '@/services/chat.service';
import { useAuth } from '@/providers/auth-provider';

export function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { user } = useAuth();
  const pathname = usePathname();
  const [currentContext, setCurrentContext] = useState('');

  // 1. Detect context changes (e.g., navigating from public home to researcher dashboard)
  useEffect(() => {
    let newContext = 'public';
    if (pathname.includes('/owner') || (pathname === '/dashboard' && user?.role === 'owner')) {
      newContext = 'owner';
    } else if (pathname.includes('/researcher') || (pathname === '/dashboard' && user?.role === 'researcher')) {
      newContext = 'researcher';
    } else if (pathname.includes('/admin') || (pathname === '/dashboard' && user?.role === 'admin')) {
      newContext = 'admin';
    }

    // If context changed, reset the chat!
    if (newContext !== currentContext) {
      setCurrentContext(newContext);
      setMessages([]); 
    }
  }, [pathname, user, currentContext]);

  // 2. Set initial welcome message based on the active context
  useEffect(() => {
    if (messages.length === 0 && currentContext) {
      let welcomeMsg = "👋 Bonjour ! Je suis OptiBot. Posez-moi vos questions sur nos services de stockage IoT !";
      
      if (currentContext === 'owner') {
        welcomeMsg = "🏭 Bonjour Propriétaire ! Je suis là pour vous aider à gérer vos entrepôts et vos locations sur ce tableau de bord.";
      } else if (currentContext === 'researcher') {
        welcomeMsg = "🔬 Bonjour Chercheur ! Besoin d'aide pour trouver l'entrepôt idéal ou calculer un score d'optimisation ici ?";
      } else if (currentContext === 'admin') {
        welcomeMsg = "⚙️ Bonjour Admin ! Prêt à superviser la plateforme OptiStock ?";
      }
      
      setMessages([{ role: 'assistant', content: welcomeMsg }]);
    }
  }, [messages.length, currentContext]);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (isOpen && messagesEndRef.current) {
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  }, [messages, isOpen]);

  const toggleChat = () => setIsOpen(!isOpen);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput('');
    
    // Add user message to state
    const newMessages: ChatMessage[] = [...messages, { role: 'user', content: userMsg }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      // Optibot API call with currentPath
      const response = await chatService.sendMessage(userMsg, messages, pathname);
      setMessages([...newMessages, { role: 'assistant', content: response }]);
    } catch (error) {
      setMessages([
        ...newMessages, 
        { role: 'assistant', content: "Désolé, je rencontre des difficultés techniques pour vous répondre en ce moment." }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      
      {/* Chat Window */}
      {isOpen && (
        <div className="bg-white rounded-2xl shadow-2xl w-80 sm:w-96 h-[500px] flex flex-col overflow-hidden border border-gray-200 mb-4 transition-all duration-300 ease-in-out">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-4 flex justify-between items-center shadow-md z-10">
            <div className="flex items-center gap-2">
              <div className="bg-white/20 p-1.5 rounded-full">
                <span className="text-xl">🤖</span>
              </div>
              <div>
                <h3 className="font-bold text-sm">OptiBot</h3>
                <p className="text-xs text-blue-100">Assistant IA</p>
              </div>
            </div>
            <button 
              onClick={toggleChat}
              className="text-white hover:text-gray-200 focus:outline-none bg-white/10 hover:bg-white/20 p-1 rounded-md transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 bg-gray-50 flex flex-col gap-4">
            {messages.map((msg, index) => (
              <div 
                key={index} 
                className={`flex gap-2 max-w-[85%] ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm border border-blue-200">
                    🤖
                  </div>
                )}
                
                <div 
                  className={`p-3 rounded-2xl text-sm shadow-sm ${
                    msg.role === 'user' 
                      ? 'bg-blue-600 text-white rounded-tr-none' 
                      : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none'
                  }`}
                  style={{ whiteSpace: 'pre-wrap' }}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex gap-2 max-w-[85%] mr-auto">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  🤖
                </div>
                <div className="bg-white border border-gray-100 p-4 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-3 bg-white border-t border-gray-200">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Écrivez votre message..."
                className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                disabled={isLoading}
              />
              <button 
                type="submit" 
                disabled={!input.trim() || isLoading}
                className="bg-blue-600 text-white w-10 h-10 rounded-full flex items-center justify-center hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-0.5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Floating Action Button */}
      <button
        onClick={toggleChat}
        className={`w-14 h-14 rounded-full bg-blue-600 text-white shadow-xl flex items-center justify-center hover:bg-blue-700 hover:scale-105 transition-all duration-300 border-2 border-white focus:outline-none focus:ring-4 focus:ring-blue-300 ${isOpen ? 'rotate-90 scale-90 opacity-0 pointer-events-none absolute' : 'rotate-0 opacity-100'}`}
      >
        <span className="text-3xl drop-shadow-sm">🤖</span>
      </button>
      
      {/* Close button that replaces FAB when open */}
      <button
        onClick={toggleChat}
        className={`w-14 h-14 rounded-full bg-gray-800 text-white shadow-xl flex items-center justify-center hover:bg-gray-900 hover:scale-105 transition-all duration-300 border-2 border-white focus:outline-none focus:ring-4 focus:ring-gray-300 ${!isOpen ? '-rotate-90 scale-90 opacity-0 pointer-events-none absolute' : 'rotate-0 opacity-100'}`}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}
