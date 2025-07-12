import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from datetime import datetime
import random
import sys
from test_PopUp import PopUp
from PyQt5.QtWidgets import QApplication

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ Errore: Imposta la variabile d'ambiente GEMINI_API_KEY")
    exit()

genai.configure(api_key=api_key)

# IT's time to create some tools for our agent!
#--------------------------------TOOLS--------------------------------
class Tool:
    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func

    @staticmethod
    def get_weather(city: str) -> str:
        weather_data = {
            "Milano": "Temperatura: 18°C, Condizioni: Nuvoloso, Umidità: 75%",
            "Roma": "Temperatura: 22°C, Condizioni: Soleggiato, Umidità: 60%",
            "Napoli": "Temperatura: 24°C, Condizioni: Parzialmente nuvoloso, Umidità: 70%",
            "Torino": "Temperatura: 16°C, Condizioni: Pioggia leggera, Umidità: 85%"
        }
        return weather_data.get(city, f"Dati meteo per {city}: Temperatura: 20°C, Condizioni: Dati non disponibili")

    @staticmethod
    def somma(num1: float, num2: float) -> float:
        """Esegue la somma di due numeri"""
        return num1 + num2

    @staticmethod
    def pop_up():
        """Mostra un popup"""
        # verifica se QApplication è gia in esecuzione
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        try:
            popup = PopUp()
            popup.show()
            
            if not app.activeWindow():
                popup.exec_()
        except Exception as e:
            print(f"❌ Errore durante la visualizzazione del popup: {e}")


# classe agente AI
class AgentAI:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.chat_history = []
        self.conv_file = "conversation_history.json"
        self.load_conversation_history()

    def _serialize_message(self, message):
        """Converte un messaggio in un formato serializzabile"""
        if hasattr(message, 'role') and hasattr(message, 'parts'):
            return {
                'role': message.role,
                'parts': [{'text': part.text} for part in message.parts if hasattr(part, 'text')]
            }
        return message

    def _deserialize_message(self, message_data):
        """Converte i dati del messaggio in un formato utilizzabile dal modello"""
        if isinstance(message_data, dict):
            return message_data
        return message_data

    def load_conversation_history(self):
        """Carica la cronologia della conversazione da un file JSON."""
        try:
            if os.path.exists(self.conv_file):
                with open(self.conv_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        print("📝 File cronologia vuoto, inizializzazione nuova cronologia")
                        self.chat_history = []
                        return
                    
                    data = json.loads(content)
                    
                    # Carica la cronologia e deserializza i messaggi
                    raw_history = data.get('history', [])
                    self.chat_history = [self._deserialize_message(msg) for msg in raw_history]
                    
                    print(f"🔄 Cronologia della conversazione caricata: {len(self.chat_history)} messaggi")
        except json.JSONDecodeError as e:
            print(f"❌ Errore JSON nella cronologia: {e}")
            self._handle_corrupted_file()
        except Exception as e:
            print(f"❌ Errore nel caricamento della cronologia: {e}")
            self._handle_corrupted_file()

    def _handle_corrupted_file(self):
        """Gestisce i file corrotti creando un backup e resettando la cronologia"""
        if os.path.exists(self.conv_file):
            backup_name = f"{self.conv_file}.corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                os.rename(self.conv_file, backup_name)
                print(f"📁 File corrotto spostato in: {backup_name}")
            except Exception as e:
                print(f"❌ Errore nel backup del file corrotto: {e}")
        self.chat_history = []
        print("✅ Cronologia resettata")
    
    def save_conversation_history(self):
        """Salva la cronologia della conversazione in un file JSON."""
        try:
            # Serializza i messaggi per il salvataggio
            serialized_history = [self._serialize_message(msg) for msg in self.chat_history]
            
            data = {
                'last_updated': datetime.now().isoformat(),
                'history': serialized_history
            }
            
            # Salva in un file temporaneo prima di sovrascrivere quello principale
            temp_file = f"{self.conv_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Se il salvataggio è riuscito, sostituisci il file principale
            if os.path.exists(self.conv_file):
                os.remove(self.conv_file)
            os.rename(temp_file, self.conv_file)
            
            print(f"💾 Cronologia salvata con successo ({len(self.chat_history)} messaggi)")
            
        except Exception as e:
            print(f"❌ Errore nel salvataggio della cronologia: {e}")
            # Rimuovi il file temporaneo se esiste
            temp_file = f"{self.conv_file}.tmp"
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    def send_message(self, user_message):
        """Invia un messaggio all'agente e ottiene una risposta."""
        try:
            chat_session = self.model.start_chat(history=self.chat_history)

            # Invia il messaggio 
            response = chat_session.send_message(user_message)

            # Aggiorna cronologia
            self.chat_history = chat_session.history

            # Salva automaticamente
            self.save_conversation_history()

            return response.text
        
        except Exception as e:
            print(f"❌ Errore durante l'invio del messaggio: {e}")
            return "Si è verificato un errore durante l'elaborazione della richiesta."
    
    def clear_history(self):
        """Cancella la cronologia"""
        self.chat_history = []
        if os.path.exists(self.conv_file):
            try:
                os.remove(self.conv_file)
                print("🗑️ Cronologia della conversazione cancellata.")
            except Exception as e:
                print(f"❌ Errore nella cancellazione del file: {e}")
        else:
            print("🗑️ Cronologia della conversazione cancellata.")
    
    def fix_corrupted_history(self):
        """Rimuove il file cronologia corrotto e ricomincia"""
        if os.path.exists(self.conv_file):
            backup_name = f"{self.conv_file}.corrupted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                os.rename(self.conv_file, backup_name)
                print(f"📁 File corrotto spostato in: {backup_name}")
            except Exception as e:
                print(f"❌ Errore nel backup: {e}")
        self.chat_history = []
        print("✅ Cronologia resettata")

    def show_stats(self):
        """Mostra le statistiche della conversazione"""
        user_messages = len([msg for msg in self.chat_history if 
                           (hasattr(msg, 'role') and msg.role == 'user') or 
                           (isinstance(msg, dict) and msg.get('role') == 'user')])
        agent_messages = len([msg for msg in self.chat_history if 
                            (hasattr(msg, 'role') and msg.role == 'model') or 
                            (isinstance(msg, dict) and msg.get('role') == 'model')])
        print(f"📊 Statistiche della conversazione:\n- Messaggi utente: {user_messages}\n- Risposte dell'agente: {agent_messages}")


def main():
    """Funzione principale"""
    chat = AgentAI()
    print("👋 Benvenuto nell'UI Agent! Digita 'exit' per uscire.")
    print(
        'Ci sono 5 comandi speciali:' \
        '\n- "clear" per cancellare la cronologia' \
        '\n- "stats" per visualizzare le statistiche della conversazione' \
        '\n- "fix" cancella la cronologia corrotta' \
        '\n- "tools" strumenti disponibili' \
        '\n- "exit" per uscire'
    )
    
    # Loop conversazione 
    while True:
        try:
            user_input = input("\n💬 Tu: ").strip()

            if user_input.lower() == 'exit':
                print("👋 Arrivederci!")
                break
            elif user_input.lower() == 'clear':
                chat.clear_history()
                continue
            elif user_input.lower() == 'stats':
                chat.show_stats()
                continue
            elif user_input.lower() == 'fix':
                chat.fix_corrupted_history()
                continue
            elif user_input.lower() == 'tools':
                Tool.pop_up()
                continue
            elif not user_input:
                continue
                
            # Invia il messaggio e ottieni la risposta
            response = chat.send_message(user_input)
            print(f"\n🤖 Agente: {response}")

        except KeyboardInterrupt:
            print("\n👋 Arrivederci!")
            break
        except Exception as e:
            print(f"❌ Errore: {e}")


if __name__ == "__main__":
    main()
