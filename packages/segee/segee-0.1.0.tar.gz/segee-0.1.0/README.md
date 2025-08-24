# 🌳 Segee

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)


Lightning-fast range queries with O(log n) performance and modern Python design.


## ✨ Features

🚀 **High Performance** - O(log n) range queries and updates  
🔒 **Type Safe** - Complete generic type hints for Python 3.12+  
🏢 **Enterprise Ready** - Comprehensive error handling and validation  
🧪 **Battle Tested** - 152 unit tests with ground truth validation  
🐍 **Pythonic** - Full sequence protocol support (`tree[i]`, `len(tree)`, etc.)  
⚡ **Zero Dependencies** - Pure Python with no external requirements  

## 🚀 Quick Start

```python
from segee import SumSegmentTree, MinSegmentTree, MaxSegmentTree

# Sum queries - perfect for range sum problems
sum_tree = SumSegmentTree(1000)
sum_tree[100] = 42
sum_tree[200] = 58
print(sum_tree.sum(100, 201))  # 100

# Min/Max queries - ideal for range minimum/maximum problems  
min_tree = MinSegmentTree(1000)
min_tree[50:55] = [10, 5, 20, 15, 8]
print(min_tree.minimum(50, 55))  # 5

# Custom operations - build your own segment tree
import operator, math
gcd_tree = SegmentTree(100, 0, math.gcd)
```

## 📦 Installation

```bash
pip install segee
```

## 🏗️ Architecture

```
segee/
├── segment_tree/           # Segment tree implementations
│   ├── segment_tree.py    # Generic segment tree core
│   └── specialized.py     # Sum/Min/Max convenience classes
├── exceptions.py          # Custom exception hierarchy  
└── _types.py             # Type definitions and protocols
```


## 📚 Documentation

- **[Usage Guide](docs/usage.md)** - Comprehensive examples and patterns
- **[API Reference](docs/api.md)** - Complete method documentation  
- **[Performance](docs/performance.md)** - Benchmarks and complexity analysis
- **[Contributing](docs/contributing.md)** - Development setup and guidelines



## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for the Python community**

[🐛 Report Bug](https://github.com/nodashin/segee/issues) • [✨ Request Feature](https://github.com/nodashin/segee/issues) • [📖 Documentation](docs/)

</div>