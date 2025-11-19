from aqt import mw, gui_hooks
from aqt.utils import showInfo, qconnect
from aqt.qt import QAction

def flag_three_correct_cards():
    deck_id = mw.col.decks.get_current_id()
    deck_name = mw.col.decks.name(deck_id)
    
    query = f'"deck:{deck_name}"'
    card_ids = mw.col.find_cards(query)
    
    cards_to_flag = []
    
    for card_id in card_ids:
        card_data = mw.col.db.first("SELECT id, flags FROM cards WHERE id = ?", card_id)
        
        if card_data and card_data[1] == 4:
            print("Skipping lower-order cards")
            continue
        
        reviews = mw.col.db.all(
            "SELECT ease FROM revlog WHERE cid = ? ORDER BY id DESC LIMIT 3",
            card_id
        )
        
        if len(reviews) >= 3:
            last_three = [r[0] for r in reviews]
            
            if all(ease >= 2 for ease in last_three):
                cards_to_flag.append(card_id)
    
    # Use the new API - flag all cards at once
    if cards_to_flag:
        mw.col.set_user_flag_for_cards(3, cards_to_flag)  # 1 = Red flag
    
    # Refresh the browser if it's open
    if hasattr(mw, 'browser') and mw.browser:
        mw.browser.model.reset()
    
    showInfo(f"Flagged {len(cards_to_flag)} ready to be merged!")

def setup_menu():
    action = QAction("Check encoding opportunities", mw)
    qconnect(action.triggered, flag_three_correct_cards)
    mw.form.menuTools.addAction(action)

gui_hooks.profile_did_open.append(setup_menu)
