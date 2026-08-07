import os
import time
import asyncio
from storage.manager import StorageManager

async def agent_loop():
    storage = StorageManager()
    print("Agent OSINT autonome démarré. Attente de requêtes...")
    
    while True:
        # Vérification du signal d'arrêt d'urgence
        if os.path.exists("storage/STOP_SIGNAL"):
            print("Signal d'arrêt d'urgence détecté. Interruption propre.")
            os.remove("storage/STOP_SIGNAL")
            break
            
        # Exemple de boucle de traitement
        # L'Agent A génère des requêtes de recherche et interroge SQLite/FTS5
        results = storage.search_fts("Registre Commerce", limit=5)
        
        # Pause active du cycle d'investigation
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(agent_loop())
