# SDN Controllers with POX — Lab 3

Multi-path routing on a **diamond topology** with a custom [POX](https://github.com/noxrepo/pox) controller, emulated in Mininet with Open vSwitch.

Author: Abderraouf Atsamnia

## Topology

Four switches (s1–s4) form a diamond, each with one host:

| Host  | MAC                 | IP            | Switch |
|-------|---------------------|---------------|--------|
| host1 | 00:00:00:00:10:01   | 10.0.10.1/24  | s1     |
| host2 | 00:00:00:00:20:01   | 10.0.20.1/24  | s2     |
| host3 | 00:00:00:00:30:01   | 10.0.30.1/24  | s3     |
| host4 | 00:00:00:00:40:01   | 10.0.40.1/24  | s4     |

Links: s1–s2, s2–s3, s3–s4, s4–s1. s1 and s2 are handled by a reference controller (port 6634); s3 and s4 are controlled by the custom POX component (port 6633).

## Repository content

| Path | Description |
|------|-------------|
| `solution/tp.py` | My POX component (`misc.tp`): per-switch flow installation with idle/hard timeouts, direct neighbour routing, and use of the "upper" link otherwise |
| `solution/diamond.py` | Mininet script building the diamond topology and launching the controllers |
| `solution/passerelle.py` | Mininet script for the gateway (fake gateways) part |
| `original/` | Starting files provided with the lab |
| `Screenshots/` | S01–S22: screenshots of the experiments |
| `evidence.png` | Additional evidence screenshot |
| `abderraouf_atsamnia_lab3.pdf` | **Final report** |
| `abderraouf_atsamnia_lab3_excel.xlsx` | Measurements spreadsheet |
| `Lab 3.pdf` | Lab statement |

## How to run

1. Copy `solution/tp.py` to `~/pox/pox/misc/tp.py`.
2. Run the topology (as root, inside the Mininet VM):
   ```bash
   sudo python3 solution/diamond.py
   ```
3. In the Mininet CLI, test connectivity and flows:
   ```
   mininet> pingall
   mininet> host1 ping -c 3 host3
   mininet> sh ovs-ofctl dump-flows s3
   ```

## How the controller works

- On connection, each switch maps its port names (`sX-ethN`) to port numbers.
- Switches s3 and s4 forward packets by destination MAC: to their local host, to a direct neighbour, or through the upper link; flows are installed with `idle_timeout=10` and `hard_timeout=30`.
- Other switches behave as classic learning switches.

See the report PDF for the full analysis and screenshots.
