# k9s - Kubernetes CLI Dashboard

[k9s](https://github.com/derailed/k9s) is a terminal-based UI to interact with your Kubernetes clusters. It makes it easy to navigate, observe, and manage your applications.

## Installation

Download the k9s binary for your platform:

```bash
# Linux (amd64)
curl -sL "https://github.com/derailed/k9s/releases/download/v0.50.18/k9s_Linux_amd64.tar.gz" | tar -xz k9s

# macOS (Intel)
curl -sL "https://github.com/derailed/k9s/releases/download/v0.50.18/k9s_Darwin_amd64.tar.gz" | tar -xz k9s

# macOS (Apple Silicon)
curl -sL "https://github.com/derailed/k9s/releases/download/v0.50.18/k9s_Darwin_arm64.tar.gz" | tar -xz k9s
```

Or use the provided script after downloading:

```bash
cd tools/k9s
./run-k9s.sh
```

## Quick Start

```bash
# Run k9s (uses current kubectl context)
./k9s

# Run k9s for a specific namespace
./k9s -n hello-world

# Run k9s for a specific context
./k9s --context arn:aws:eks:eu-west-1:753916465480:cluster/esade-teaching
```

## Key Navigation

### Global Commands

| Key | Action |
|-----|--------|
| `:` | Command mode (type resource name) |
| `/` | Filter/search |
| `?` | Show help |
| `Ctrl+a` | Show all available aliases |
| `Esc` | Back / Clear |
| `Ctrl+c` | Exit k9s |

### Resource Navigation

| Command | Description |
|---------|-------------|
| `:pod` or `:po` | View pods |
| `:deploy` or `:dp` | View deployments |
| `:svc` or `:service` | View services |
| `:ns` or `:namespace` | View namespaces |
| `:node` or `:no` | View nodes |
| `:ctx` or `:context` | Switch context |
| `:log` | View logs |

### Actions on Resources

| Key | Action |
|-----|--------|
| `Enter` | View/Describe resource |
| `d` | Describe selected resource |
| `l` | View logs (for pods) |
| `s` | Shell into container |
| `e` | Edit resource |
| `Ctrl+d` | Delete resource |
| `y` | YAML view |
| `p` | Previous (logs) |
| `f` | Port-forward |

### Filtering

| Key | Action |
|-----|--------|
| `/` | Start filter |
| `/hello` | Filter resources containing "hello" |
| `/-l app=hello` | Filter by label |
| `Esc` | Clear filter |

## Common Workflows

### View hello-world deployment

```
1. Start k9s: ./k9s
2. Type :ns and press Enter
3. Select hello-world namespace
4. Type :deploy to see deployments
5. Press Enter on hello-world to see details
```

### View pod logs

```
1. Start k9s: ./k9s -n hello-world
2. Type :pod and press Enter
3. Select a pod
4. Press 'l' to view logs
5. Press 'p' to see previous container logs
6. Press '0' for all containers, '1' for first, etc.
```

### Shell into a pod

```
1. Navigate to pods (:pod)
2. Select a pod
3. Press 's' to open shell
4. Type 'exit' to leave shell
```

### Scale deployment

```
1. Navigate to deployments (:deploy)
2. Select hello-world
3. Press 's' to scale
4. Enter new replica count
```

### Port-forward to a service

```
1. Navigate to services (:svc)
2. Select hello-world
3. Press 'f' for port-forward
4. Access via localhost
```

## Color Indicators

| Color | Meaning |
|-------|---------|
| Green | Healthy/Running |
| Yellow | Warning/Pending |
| Red | Error/Failed |
| Gray | Terminating |

## Resource Status Icons

| Icon | Status |
|------|--------|
| ● | Running |
| ◌ | Pending |
| ✘ | Failed |
| ◎ | Succeeded |

## Tips

1. **Quick namespace switch**: Press `0-9` to switch between recent namespaces
2. **Pulse view**: Type `:pulse` to see cluster activity
3. **XRay view**: Type `:xray deploy` to see deployment tree
4. **Popeye**: Type `:popeye` to scan cluster for issues
5. **Benchmarks**: Press `b` on a service to run HTTP benchmarks

## Configuration

k9s stores configuration in `~/.config/k9s/`:

- `config.yaml` - General settings
- `skins/` - Custom color themes
- `hotkeys.yaml` - Custom key bindings
- `plugins.yaml` - Custom plugins

## Links

- [k9s GitHub](https://github.com/derailed/k9s)
- [k9s Documentation](https://k9scli.io/)
- [k9s Releases](https://github.com/derailed/k9s/releases)
