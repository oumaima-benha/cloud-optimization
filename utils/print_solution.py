#Fonction d'affichage de solution
def afficher_placement(placement):
    if not placement.placement:
        print("⚠️ Aucun service placé.")
        return

    # --- Affichage des placements par service ---
    print("\n🖥️  Services placés :")
    for s_id, (m_id, r_id) in placement.placement.items():
        red = placement.redundancy.get(s_id, 1)
        print(f"  - {s_id:<5s} → Machine: {m_id:<10s} | Région: {r_id:<5s} | Redondance: {red}")

    # --- Affichage du chiffrement des flux ---
    if placement.encryption:
        print("\n Chiffrement des flux :")
        for (src, dst), enc in placement.encryption.items():
            status = "✅" if enc else "❌"
            print(f"  - {src} → {dst} : {status}")
    else:
        print("\n Aucun flux configuré pour le chiffrement.")

    print("=====================================\n")