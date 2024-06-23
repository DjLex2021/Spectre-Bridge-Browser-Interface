import requests
import time
from threading import Thread
from collections import defaultdict

METRIC_NAMES = {
    "spr_blocks_mined": "Blocks Mined",
    "spr_valid_share_counter": "Valid Share",
    "spr_worker_errors": "Worker Errors",
    "spr_invalid_share_counter": "Invalid Share",
    "spr_valid_share_diff_counter": "Valid Share Difficulty",
    "spr_worker_job_counter": "Job Counter"
}

METRIC_ORDER = [
    "Blocks Mined",
    "Valid Share",
    "Invalid Share",
    "Max Valid Share Difficulty",
    "Job Counter"
]

def fetch_metrics():
    while True:
        url = 'http://localhost:2114/metrics'
        response = requests.get(url)
        if response.status_code == 200:
            metrics_by_wallet_device = defaultdict(lambda: defaultdict(dict))
            total_metrics_by_wallet = defaultdict(lambda: defaultdict(int))
            max_difficulty_by_wallet = defaultdict(int)
            blocks_mined_by_wallet = defaultdict(int)
            devices_by_wallet = defaultdict(set)
            network_hashrate = 0.0
            network_difficulty = 0.0

            for line in response.text.split('\n'):
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.split(' ')
                if len(parts) == 2:
                    metric, value = parts
                    metric_base = metric.split('{')[0]
                    if metric_base == "spr_estimated_network_hashrate_gauge":
                        network_hashrate = int(float(value))
                    elif metric_base == "spr_network_difficulty_gauge":
                        network_difficulty = int(float(value))
                    metric_name = METRIC_NAMES.get(metric_base, None)
                    if not metric_name:
                        continue
                    
                    if '{' in metric:
                        metric_info = metric.split('{')[1].split('}')[0]
                        details = {k: v.strip('"') for k, v in (item.split('=') for item in metric_info.split(','))}
                        wallet = details.get('wallet')
                        device = details.get('worker', 'Unknown')
                        ip = details.get('ip', 'Unknown')
                        
                        if wallet and device != 'tnn-dev' and device != 'Unknown':
                            key = f"{device} ({ip})"
                            metrics_by_wallet_device[wallet][key][metric_name] = int(float(value))
                            if metric_name != "Valid Share Difficulty":
                                total_metrics_by_wallet[wallet][metric_name] += int(float(value))
                            if metric_name == "Valid Share Difficulty":
                                max_difficulty_by_wallet[wallet] = max(max_difficulty_by_wallet[wallet], int(float(value)))
                            if metric_name == "Blocks Mined":
                                blocks_mined_by_wallet[wallet] += int(float(value))
                            devices_by_wallet[wallet].add(key)

            with open('metrics.html', 'w', encoding='utf-8') as f:
                f.write('<html><head><title>Hotfix Solo Pool</title>')
                f.write('<style>')
                f.write('body { font-family: Arial, sans-serif; margin: 20px; }')
                f.write('h1, h2 { color: #333; }')
                f.write('table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }')
                f.write('th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }')
                f.write('th { background-color: #f2f2f2; }')
                f.write('tr:nth-child(even) { background-color: #f9f9f9; }')
                f.write('tr:hover { background-color: #f1f1f1; }')
                f.write('.tab { cursor: pointer; padding: 10px; background-color: #fff; border: 1px solid #ddd; margin-top: 5px; }')
                f.write('.tab-content { display: none; padding: 10px; border: 1px solid #ddd; border-top: none; }')
                f.write('.total_metrics_style { padding: 20px; border: 1px solid #ccc; margin-top: 20px; }')
                f.write('.network-info { display: flex; gap: 10px; margin-bottom: 20px; }')
                f.write('.network-info div { padding: 10px 20px; background-color: #007bff; color: white; border-radius: 5px; cursor: pointer; }')
                f.write('.canvas-container { display: flex; gap: 20px; }')
                f.write('.online-indicator { color: green; margin-left: 10px; }')  # Add CSS for the ONLINE indicator
                f.write('</style>')
                f.write('<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>')
                f.write('<script>')
                f.write('function toggleTabContent(id) {')
                f.write('    var content = document.getElementById(id);')
                f.write('    if (content.style.display === "none" || content.style.display === "") {')
                f.write('        content.style.display = "block";')
                f.write('    } else {')
                f.write('        content.style.display = "none";')
                f.write('    }')
                f.write('}')
                f.write('function renderChart(ctx, labels, data, title) {')
                f.write('    new Chart(ctx, {')
                f.write('        type: "bar",')
                f.write('        data: {')
                f.write('            labels: labels,')
                f.write('            datasets: [{')
                f.write('                label: title,')
                f.write('                data: data,')
                f.write('                backgroundColor: "rgba(75, 192, 192, 0.2)",')
                f.write('                borderColor: "rgba(75, 192, 192, 1)",')
                f.write('                borderWidth: 1')
                f.write('            }]')
                f.write('        },')
                f.write('        options: {')
                f.write('            scales: {')
                f.write('                y: {')
                f.write('                    beginAtZero: true')
                f.write('                }')
                f.write('            }')
                f.write('        }')
                f.write('    });')
                f.write('}')
                f.write('</script>')
                f.write('</head><body>')
                f.write('<h1>HNP Hotfix Spectre Bridge Browser Interface <span id="last-updated" style="font-size: 0.6em; margin-left: 20px;"></span></h1>')
                
                # Convert network_hashrate and network_difficulty to MH/s and display as integers
                network_hashrate_mhs = int(network_hashrate / 1e6)
                network_difficulty_mhs = int(network_difficulty / 1e6)
                
                # Write network hashrate and difficulty as styled buttons
                f.write('<div class="network-info">')
                f.write(f'<div>Network Hashrate: {network_hashrate_mhs} MH/s</div>')
                f.write(f'<div>Network Difficulty: {network_difficulty_mhs} M</div>')
                f.write('</div>')

                for wallet, totals in total_metrics_by_wallet.items():
                    f.write(f'<div class="total_metrics_style" id="{wallet}"><h3>Total Metrics for Wallet: {wallet}<span class="online-indicator" id="{wallet}-online" style="display:none;">ONLINE</span></h3>')  # Add ONLINE indicator
                    f.write('<div class="canvas-container">')
                    
                    # General metrics except "Blocks Mined", "Valid Share Difficulty", and "Job Counter"
                    general_labels = [metric_name for metric_name in totals.keys() if metric_name not in ["Blocks Mined", "Valid Share Difficulty", "Job Counter"]]
                    general_data = [totals[metric_name] for metric_name in general_labels]
                    f.write(f'<canvas id="{wallet}-chart" width="400" height="200"></canvas>')
                    f.write('<script>')
                    f.write(f'var ctx = document.getElementById("{wallet}-chart").getContext("2d");')
                    f.write(f'var labels = {general_labels};')
                    f.write(f'var data = {general_data};')
                    f.write('renderChart(ctx, labels, data, "Metrics");')
                    f.write('</script>')

                    f.write(f'<canvas id="{wallet}-blocks-chart" width="400" height="200"></canvas>')
                    f.write('<script>')
                    f.write(f'var ctxBlocks = document.getElementById("{wallet}-blocks-chart").getContext("2d");')
                    f.write(f'var blocksLabels = ["Blocks Mined"];')
                    f.write(f'var blocksData = [{blocks_mined_by_wallet[wallet]}];')
                    f.write('renderChart(ctxBlocks, blocksLabels, blocksData, "Blocks Mined");')
                    f.write('</script>')

                    f.write(f'<canvas id="{wallet}-difficulty-chart" width="400" height="200"></canvas>')
                    f.write('<script>')
                    f.write(f'var ctxDifficulty = document.getElementById("{wallet}-difficulty-chart").getContext("2d");')
                    f.write(f'var difficultyLabels = ["Max Valid Share Difficulty"];')
                    f.write(f'var difficultyData = [{max_difficulty_by_wallet[wallet]}];')
                    f.write('renderChart(ctxDifficulty, difficultyLabels, difficultyData, "Max Valid Share Difficulty");')
                    f.write('</script>')

                    f.write('</div>')
                    f.write('<table><thead><tr><th>Metric</th><th>Total Value</th></tr></thead><tbody>')
                    
                    for metric_name in METRIC_ORDER:
                        if metric_name == "Max Valid Share Difficulty":
                            metric_value = max_difficulty_by_wallet[wallet]
                        else:
                            metric_value = totals.get(metric_name, 0)
                        metric_id = f"{wallet}-{metric_name.replace(' ', '-')}"
                        f.write(f'<tr><td>{metric_name}</td><td id="{metric_id}">{metric_value}</td></tr>')

                    f.write('</tbody></table>')
                    device_names = ', '.join(sorted(devices_by_wallet[wallet]))
                    f.write(f'<p>Connected Devices ({len(devices_by_wallet[wallet])}): {device_names}</p>')
                    f.write('</div>')

                for wallet, devices in metrics_by_wallet_device.items():
                    f.write(f'<div class="tab" onclick="toggleTabContent(\'{wallet}-content\')">Wallet: {wallet}</div>')
                    f.write(f'<div id="{wallet}-content" class="tab-content">')
                    for device, metrics in devices.items():
                        f.write(f'<h3>Device: {device}</h3>')
                        f.write('<table><thead><tr><th>Metric</th><th>Value</th></thead><tbody>')
                        for metric_name, value in sorted(metrics.items()):
                            metric_id = f"{wallet}-{device}-{metric_name.replace(' ', '-')}"
                            f.write(f'<tr><td>{metric_name}</td><td id="{metric_id}">{value}</td></tr>')
                        f.write('</tbody></table>')
                    f.write('</div>')
                f.write('</body><div class="footer" style="color: #6bcf54; margin-top: 30px; align: right;">Donate Hotfix: spectre:qpamev6hcxkhx3x0vjaxmgnurszln88xrn67rxcswnt27jzyxvr9ymljr3hmx</div></html>')
        else:
            print('Failed to fetch metrics')
        time.sleep(10)

def start_server():
    from http.server import SimpleHTTPRequestHandler, HTTPServer
    server_address = ('', 80)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print('Starting server on port 80...')
    httpd.serve_forever()

if __name__ == "__main__":
    Thread(target=fetch_metrics).start()
    start_server()
