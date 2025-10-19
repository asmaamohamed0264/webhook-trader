# Adaugă FUSION_TEST_MODE în Dokploy

## 🎯 **VARIABILA DE ADĂUGAT**

În Dokploy, la aplicația `webhook-trader`, în tab-ul **Environment**, adaugă această variabilă:

```bash
FUSION_TEST_MODE=true
```

## 🚀 **PAȘII:**

1. **Mergi la aplicația webhook-trader în Dokploy**
2. **Click pe tab-ul "Environment"**
3. **Adaugă variabila:**
   ```
   FUSION_TEST_MODE=true
   ```
4. **Click "Save"**
5. **Redeploy aplicația**

## 🎯 **CE VA FACE:**

- ✅ **Permite testarea** în afara orelor de piață (duminică seara)
- ✅ **Strategia va rula** chiar dacă piața este închisă
- ✅ **Poți testa** ASTS și AAPL oricând
- ✅ **Log-uri detaliate** pentru debugging

## 📊 **DUPĂ ADĂUGARE:**

Strategia va rula automat și vei vedea în log-uri:
```
📊 Fusion Pro strategy cycle for symbols: ASTS, AAPL
Processing ASTS...
Processing AAPL...
📊 Processed 2/2 symbols
```

---

**Adaugă variabila și redeploy pentru a testa strategia pe ASTS și AAPL!** 🚀
