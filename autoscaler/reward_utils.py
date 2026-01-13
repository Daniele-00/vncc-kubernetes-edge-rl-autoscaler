def reward_function(latency, replicas, low_thr, high_thr, action):
    """
    Calcola la reward per l'autoscaler RL.

    Parametri:
      latency  : latenza media osservata in questo step
      replicas : numero di pod attivi dopo l'azione
      low_thr  : soglia inferiore SLA (target "basso")
      high_thr : soglia superiore SLA (violazione SLA sopra di questa)
      action   : -1 (scale down), 0 (hold), +1 (scale up)

    La reward ha 3 componenti:
      - SLA term    : premia bassi tempi di risposta, penalizza violazione SLA
      - Cost term   : penalizza repliche extra, specialmente in LOW/TARGET
      - Shape term  : piccolo bias per azioni "sensate" (up in HIGH, down in LOW)
    """

    # --- Determina la zona di latenza ---
    if latency < low_thr:
        zone = "low"
    elif latency < high_thr:
        zone = "target"
        # target: dentro l'SLA ma non super-basso
    else:
        zone = "high"

    # --- 1) SLA TERM ---
    if zone == "high":
        # Violazione SLA: forte penalità
        sla = -10.0
    elif zone == "target":
        # Dentro la banda: meglio se più vicino a low_thr
        # frac = 1 se siamo appena sotto high_thr
        # frac = 0 se siamo appena sopra low_thr
        # In realtà vogliamo il contrario: più vicino a low_thr => meglio
        # quindi invertiamo:
        frac = (high_thr - latency) / max(1e-9, (high_thr - low_thr))  # in [0,1]
        # frac=1 => latency = low_thr   (migliore)
        # frac=0 => latency = high_thr  (peggiore)
        sla = 2.0 + 4.0 * frac  # fra ~2 e 6
    else:  # zone == "low"
        # Siamo ben al di sotto della soglia: molto buono
        sla = 7.0

    # --- 2) COST TERM (dipende dalla zona) ---
    extra = max(0, replicas - 1)

    if zone == "high":
        # quando stiamo rompendo l'SLA, il costo dei pod conta meno
        cost_weight = 0.5
    elif zone == "target":
        cost_weight = 1.0
    else:  # low
        # in calma vogliamo fortemente poche repliche
        cost_weight = 2.0

    cost = -cost_weight * extra

    # --- 3) SHAPING TERM SULL'AZIONE ---
    shape = 0.0

    if zone == "high":
        # sotto stress: incoraggio fortemente a scalare UP
        if action == 1:
            shape += 2.0

    elif zone == "low":
        # in calma: incoraggio a scalare DOWN se ho più di 1 pod
        if action == -1 and replicas > 1:
            shape += 1.0

    # in "target" nessuna spinta: decide SLA + costo

    # --- REWARD TOTALE ---
    return sla + cost + shape
