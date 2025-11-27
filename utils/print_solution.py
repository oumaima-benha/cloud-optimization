# Function to display a placement solution
def display_placement(placement):
    if not placement.placement:
        print("⚠️ No services placed.")
        return

    # --- Display placements per service ---
    print("\n🖥️  Placed services:")
    for s_id, (m_id, r_id) in placement.placement.items():
        red = placement.redundancy.get(s_id, 1)
        print(f"  - {s_id:<5s} → Machine: {m_id:<10s} | Region: {r_id:<5s} | Redundancy: {red}")

    # --- Display flow encryption ---
    if placement.encryption:
        print("\n Flow encryption status:")
        for (src, dst), enc in placement.encryption.items():
            status = "✅" if enc else "❌"
            print(f"  - {src} → {dst} : {status}")
    else:
        print("\n No flows configured for encryption.")

    print("=====================================\n")