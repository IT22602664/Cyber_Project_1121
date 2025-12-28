"""
Test All Services - Zero Trust Telehealth Platform
Tests all ML APIs, Backend, and Frontend
"""

import requests
import time
import json
from colorama import init, Fore, Style

init(autoreset=True)

def test_service(name, url, timeout=5):
    """Test if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"{Fore.GREEN}✓ {name:30} - RUNNING{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}⚠ {name:30} - RESPONDING (Status: {response.status_code}){Style.RESET_ALL}")
            return True
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ {name:30} - NOT RUNNING{Style.RESET_ALL}")
        return False
    except requests.exceptions.Timeout:
        print(f"{Fore.YELLOW}⚠ {name:30} - TIMEOUT{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}✗ {name:30} - ERROR: {str(e)}{Style.RESET_ALL}")
        return False

def main():
    print("\n" + "="*70)
    print(f"{Fore.CYAN}🧪 ZERO TRUST TELEHEALTH PLATFORM - SERVICE TEST{Style.RESET_ALL}")
    print("="*70 + "\n")
    
    services = [
        ("Voice API (Port 8001)", "http://localhost:8001/health"),
        ("Keystroke API (Port 8002)", "http://localhost:8002/health"),
        ("Mouse API (Port 8003)", "http://localhost:8003/health"),
        ("Backend Server (Port 5000)", "http://localhost:5000/api/health"),
        ("Frontend App (Port 5173)", "http://localhost:5173"),
    ]
    
    results = []
    
    print(f"{Fore.CYAN}Testing Services...{Style.RESET_ALL}\n")
    
    for name, url in services:
        result = test_service(name, url)
        results.append((name, result))
        time.sleep(0.5)
    
    print("\n" + "="*70)
    print(f"{Fore.CYAN}📊 SUMMARY{Style.RESET_ALL}")
    print("="*70 + "\n")
    
    running = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"Services Running: {Fore.GREEN}{running}/{total}{Style.RESET_ALL}")
    
    if running == total:
        print(f"\n{Fore.GREEN}✅ ALL SERVICES ARE RUNNING!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}🌐 Open the application:{Style.RESET_ALL}")
        print(f"   Frontend: http://localhost:5173")
        print(f"   Backend:  http://localhost:5000")
        print(f"\n{Fore.CYAN}📚 API Documentation:{Style.RESET_ALL}")
        print(f"   Voice API:     http://localhost:8001/docs")
        print(f"   Keystroke API: http://localhost:8002/docs")
        print(f"   Mouse API:     http://localhost:8003/docs")
    else:
        print(f"\n{Fore.YELLOW}⚠️  SOME SERVICES ARE NOT RUNNING{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Not Running:{Style.RESET_ALL}")
        for name, result in results:
            if not result:
                print(f"   - {name}")
        print(f"\n{Fore.CYAN}💡 Tip:{Style.RESET_ALL} Run 'start-all-services.bat' to start all services")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()

