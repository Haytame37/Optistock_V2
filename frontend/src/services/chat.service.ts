import api from './api';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export const chatService = {
  /**
   * Envoie un message au chatbot OptiBot
   */
  async sendMessage(message: string, history: ChatMessage[], currentPath: string = "/"): Promise<string> {
    try {
      const response = await api.post('/chat/', {
        message,
        history,
        current_path: currentPath
      });
      return response.data.response;
    } catch (error) {
      console.error('Erreur lors de la communication avec OptiBot:', error);
      throw error;
    }
  },
};
