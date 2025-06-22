# 🌱 Home-Garden

**Home-Garden** to inteligentny asystent do domowej uprawy roślin. Monitoruje wilgotność gleby, kontroluje oświetlenie i automatycznie podlewa rośliny, gdy tego potrzebują. Dzięki niemu Twoje rośliny będą zawsze zadbane, nawet gdy zapomnisz o podlewaniu.  
Jest to idealne rozwiązanie dla domowych miłośników zieleni, zapracowanych ogrodników i fanów elektroniki DIY.  

**Home-Garden** sprawdzi się również w dużych uprawach, dostarczając niezbędne informację o uprawach w czasie rzeczywistym.

Projekt opiera się m.in. na rozwiązaniu [**Logdash.io**](https://logdash.io), które świetnie sprawdza się w zastosowaniach IoT – umożliwia przechowywanie i wygodny podgląd danych z czujników w czasie rzeczywistym.

---

# 🔧 Instalacja

Proces instalacji jest obecnie dość złożony i wymaga ręcznej konfiguracji kilku komponentów (Raspberry Pi, Arduino, czujniki, Logdash, itp.).  
~~Pracuję nad uproszczeniem całego procesu i udostępnieniem gotowego przewodnika krok po kroku.~~

Od wersji **1.0.6036** instalację można wykonać za pomocą poniższej komendy.  
```bash
curl -sSL https://raw.githubusercontent.com/kaktus283/home-garden/main/install.sh | bash
```

**W planach:**
- Instrukcja instalacji krok po kroku  
- Gotowe obrazy firmware 
- Automatyczna konfiguracja po stronie serwera

---

# 🔄 Aktualizacje OTA (Over-the-Air)

~~Aktualizacja systemu w obecnym stanie może być jeszcze bardziej wymagająca niż sama instalacja – dotyczy to zarówno firmware'u urządzeń, jak i konfiguracji backendu.~~

~~Docelowo planuję wdrożyć uproszczony mechanizm aktualizacji OTA (Over-the-Air) oraz automatyczne sprawdzanie wersji.~~

Od wersji **1.0.1000** aktualizację OTA można wykonać za pomocą specjalnego modułu w Panelu zarządzania RaspberryPi.  
Moduł automatycznie sprawdza dostępność nowszej wersji i w razie potrzeby pobiera ją.

<p align="center">
  <img width="330" alt="image" src="https://github.com/user-attachments/assets/2090201f-59f0-470a-a3b5-7fa5468a88a3" />
</p>

---

# 📄 Licencja

(Licencja zostanie określona w przyszłości.)

---

# 🤝 Współpraca

Chcesz pomóc rozwinąć projekt? Super!  
Planuję stworzyć roadmapę i otworzyć zgłoszenia (issues), które będzie można współdzielić i rozwijać. Pull requesty mile widziane.

**Sugestie, poprawki i opinie są bardzo cenne – śmiało pisz!**
