client_id = os.getenv('CLIENT_ID')
if client_id is None:
    client_id = 'mqtt_mold_detector_default'
print(f'client_id = {client_id}')
