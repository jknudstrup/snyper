from config.config import config

def wait_for_interrupt():
    from rp2 import bootsel_button
    from machine import Pin
    import time

    led = Pin('LED', Pin.OUT)
    led.on()

    # Monitor bootsel_button for 3 seconds
    start_time = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start_time) < 3000:
        if bootsel_button() == 1:
            # Set node_id to 'disable' in config.json
            import json
            with open('config/config.json', 'r') as f:
                config_data = json.load(f)
            config_data['node_id'] = 'disable'
            config_data['foo'] = 'bar'
            with open('config/config_foo.json', 'w') as f:
                json.dump(config_data, f)

            led.off()
            return True
        time.sleep_ms(10)  # Small delay to prevent busy waiting

    led.off()
    return False


def main():
    if config.node_id == "disable":
        print("🚫 Device disabled - terminating to prevent auto-start")
        return
    
    should_abort = wait_for_interrupt()
    if should_abort: 
        print('Aborted!')
        return

    elif config.node_id == "master": 
        print('Running Master')
        from master.master import run_master
        run_master()
    else:
        print('Running Target')
        from uasyncio import run
        from target.target import run_target
        run(run_target())
        # run_target()

if __name__ == "__main__":
  main()