#!/usr/bin/env python3
"""
CogniCLI - A premium AI command line interface with Transformers and GGUF support,
with tool use, integrated lm-eval benchmarking, Synapse model support, and a dark purple accent.
"""

import sys
import os
import json
import time
import threading
import argparse
import subprocess
import warnings
import signal
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import queue
import weakref
import requests
import re

warnings.filterwarnings('ignore')

COGNICLI_ACCENT = "#800080"  # Dark purple

REQUIRED_PACKAGES = [
    'torch>=2.0.0',
    'transformers>=4.35.0',
    'huggingface-hub>=0.17.0',
    'rich>=13.0.0',
    'colorama>=0.4.6',
    'requests>=2.31.0',
    'psutil>=5.9.0',
    'pyyaml>=6.0',
    'numpy>=1.24.0',
    'tokenizers>=0.14.0',
    'accelerate>=0.24.0',
    'sentencepiece>=0.1.99',
    'protobuf>=4.24.0',
    'lm-eval>=0.4.0'
]

OPTIONAL_PACKAGES = {
    'bitsandbytes': 'bitsandbytes>=0.41.0',
    'llama_cpp': 'llama-cpp-python>=0.2.0',
}

def install_dependencies():
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package.split('>=')[0].replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def install_optional_dependency(package_key: str) -> bool:
    try:
        if package_key == 'bitsandbytes':
            import bitsandbytes
            return True
        elif package_key == 'llama_cpp':
            from llama_cpp import Llama
            return True
        return False
    except ImportError:
        try:
            package = OPTIONAL_PACKAGES[package_key]
            print(f"Installing optional dependency: {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            return True
        except Exception as e:
            print(f"Failed to install {package}: {e}")
            return False

BNB_AVAILABLE = False
GGUF_AVAILABLE = False

def check_optional_imports():
    global BNB_AVAILABLE, GGUF_AVAILABLE
    try:
        import bitsandbytes as bnb
        BNB_AVAILABLE = True
        print(f"✅ bitsandbytes {bnb.__version__} available for quantization")
    except ImportError:
        BNB_AVAILABLE = False
        print("⚠️  bitsandbytes not available - quantization disabled")
    except Exception as e:
        BNB_AVAILABLE = False
        print(f"⚠️  Error checking bitsandbytes: {e}")
        
    try:
        from llama_cpp import Llama
        GGUF_AVAILABLE = True
        print("✅ llama-cpp-python available for GGUF models")
    except ImportError:
        GGUF_AVAILABLE = False
        print("⚠️  llama-cpp-python not available - GGUF support disabled")
    except Exception as e:
        GGUF_AVAILABLE = False
        print(f"⚠️  Error checking llama-cpp-python: {e}")

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.live import Live
    from rich import box
    from rich.align import Align
    from rich.layout import Layout
    from rich.prompt import Prompt, Confirm
    from rich.status import Status
    from rich.traceback import install as install_traceback
    import torch
    import transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
    from huggingface_hub import HfApi, list_models, model_info, hf_hub_download
    import requests
    import psutil
    import yaml
    import numpy as np
    from colorama import init, Fore, Style
    try:
        check_optional_imports()
    except Exception as e:
        print(f"Warning: Could not check optional imports: {e}")
except ImportError:
    install_dependencies()
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.live import Live
    from rich import box
    from rich.align import Align
    from rich.layout import Layout
    from rich.prompt import Prompt, Confirm
    from rich.status import Status
    from rich.traceback import install as install_traceback
    import torch
    import transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
    from huggingface_hub import HfApi, list_models, model_info, hf_hub_download
    import requests
    import psutil
    import yaml
    import numpy as np
    from colorama import init, Fore, Style
    try:
        check_optional_imports()
    except Exception as e:
        print(f"Warning: Could not check optional imports: {e}")

# Install rich traceback handler for better error display
try:
    install_traceback()
except Exception as e:
    print(f"Warning: Could not install traceback handler: {e}")

try:
    init()
except Exception as e:
    print(f"Warning: Could not initialize colorama: {e}")

try:
    console = Console()
except Exception as e:
    print(f"Warning: Could not initialize Rich console: {e}")
    # Fallback to basic console
    class BasicConsole:
        def print(self, *args, **kwargs):
            print(*args, **kwargs)
        def status(self, *args, **kwargs):
            return DummyStatus()
    
    class DummyStatus:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    
    console = BasicConsole()

LOGO = """
████╗  ██████╗  ██████╗  ███╗   ██╗██╗ ██████╗██╗     ██╗
██╔═╗  ██╔═══██╗██╔════╝  ████╗  ██║██║██╔════╝██║     ██║
██║    ╚██║   ██║██║  ███╗██╔██╗ ██║██║██║     ██║     ██║
██║    ╚██║   ██║██║   ██║██║╚██╗██║██║██║     ██║     ██║
╚████╔╝ ╚██████╔╝╚██████╔╝██║ ╚████║██║╚██████╗███████╗██║
 ╚═══╝   ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚═════╝╚══════╝╚═╝
"""

@dataclass
class ModelConfig:
    name: str
    model_type: str
    precision: str
    context_length: int
    temperature: float
    top_p: float
    max_tokens: int
    device: str = "auto"
    trust_remote_code: bool = True
    use_fast_tokenizer: bool = True
    load_in_8bit: bool = False
    load_in_4bit: bool = False
    torch_dtype: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None

class ModelManager:
    """Enhanced model management with proper state tracking and error recovery"""
    
    def __init__(self, console: Console):
        self.console = console
        self.models: Dict[str, ModelConfig] = {}
        self.current_model_id: Optional[str] = None
        self.current_model: Optional[Any] = None
        self.current_tokenizer: Optional[Any] = None
        self.model_lock = threading.Lock()
        
        try:
            # Add timeout to prevent hanging
            import os
            os.environ['HF_HUB_DOWNLOAD_TIMEOUT'] = '30'
            os.environ['HF_HUB_OFFLINE'] = '0'
            self.api = HfApi()
        except Exception as e:
            print(f"Warning: Could not initialize HuggingFace API: {e}")
            self.api = None
            
        try:
            self.cache_dir = Path.home() / '.cognicli'
            self.cache_dir.mkdir(exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create cache directory: {e}")
            self.cache_dir = Path.cwd() / '.cognicli'
            try:
                self.cache_dir.mkdir(exist_ok=True)
            except Exception as e2:
                print(f"Warning: Could not create fallback cache directory: {e2}")
                self.cache_dir = None
    
    def get_current_config(self) -> Optional[ModelConfig]:
        """Get the current model configuration safely"""
        if self.current_model_id and self.current_model_id in self.models:
            return self.models[self.current_model_id]
        return None
    
    def is_model_loaded(self) -> bool:
        """Check if a model is currently loaded and ready - FIXED VERSION"""
        if self.current_model is None or self.current_model_id is None:
            return False
        
        config = self.get_current_config()
        if not config:
            return False
            
        if config.model_type == "gguf":
            # GGUF models (loaded via llama-cpp) don't have a separate tokenizer object
            return self.current_model is not None
        else:
            # For Transformers models, we need both model and tokenizer
            return self.current_model is not None and self.current_tokenizer is not None
    
    def unload_current_model(self):
        """Safely unload the current model and free memory"""
        with self.model_lock:
            if self.current_model is not None:
                # Clear CUDA cache if using GPU
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                # Delete model references
                del self.current_model
                self.current_model = None
                
            if self.current_tokenizer is not None:
                del self.current_tokenizer
                self.current_tokenizer = None
                
            self.current_model_id = None
            self.console.print("[yellow]Model unloaded and memory freed.[/yellow]")
    
    def load_model(self, model_id: str, **kwargs) -> bool:
        """Load a model with enhanced error handling and recovery"""
        try:
            with self.model_lock:
                # Unload current model first
                if self.is_model_loaded():
                    self.unload_current_model()
                
                # Create new config
                config = ModelConfig(
                    name=model_id,
                    model_type=kwargs.get('model_type', 'auto'),
                    precision=kwargs.get('precision', 'auto'),
                    context_length=kwargs.get('context_length', 2048),
                    temperature=kwargs.get('temperature', 0.7),
                    top_p=kwargs.get('top_p', 0.95),
                    max_tokens=kwargs.get('max_tokens', 512),
                    **{k: v for k, v in kwargs.items() if k not in ['model_type', 'precision', 'context_length', 'temperature', 'top_p', 'max_tokens', 'gguf_file', 'quantization']}
                )
                
                # Load the model based on type
                if config.model_type == "gguf" or kwargs.get('gguf_file'):
                    success = self._load_gguf_model(model_id, config, kwargs.get('gguf_file'))
                else:
                    success = self._load_transformers_model(model_id, config)
                
                if success:
                    self.models[model_id] = config
                    self.current_model_id = model_id
                    config.last_used = datetime.now()
                    return True
                else:
                    return False
                    
        except Exception as e:
            self.console.print(f"[red]Failed to load model: {e}[/red]")
            # Clean up on failure
            self.unload_current_model()
            return False
    
    def _load_gguf_model(self, model_id: str, config: ModelConfig, gguf_file: Optional[str] = None) -> bool:
        """Load a GGUF model with enhanced error handling"""
        try:
            if not GGUF_AVAILABLE:
                self.console.print("[red]GGUF support not available. Install llama-cpp-python.[/red]")
                return False
            
            from llama_cpp import Llama
            
            # Determine GGUF file path
            if gguf_file:
                gguf_path = Path(gguf_file)
                if not gguf_path.exists():
                    self.console.print(f"[red]GGUF file not found: {gguf_file}[/red]")
                    return False
            else:
                gguf_path = self._download_gguf_file(model_id)
                if not gguf_path:
                    return False
            
            # Load model with proper error handling
            try:
                self.current_model = Llama(
                    model_path=str(gguf_path),
                    n_ctx=config.context_length,
                    n_gpu_layers=-1 if torch.cuda.is_available() else 0,
                    verbose=False
                )
                config.model_type = "gguf"
                self.current_tokenizer = None  # GGUF models don't have separate tokenizers
                
                self.console.print(f"[bold green]✅ Loaded GGUF model:[/] {model_id}")
                self.console.print(f"[dim]File: {gguf_path.name}[/dim]")
                return True
                
            except Exception as e:
                self.console.print(f"[red]Failed to load GGUF model: {e}[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]GGUF loading error: {e}[/red]")
            return False
    
    def _load_transformers_model(self, model_id: str, config: ModelConfig) -> bool:
        """Load a Transformers model with enhanced error handling"""
        try:
            # Check if this is a Synapse model
            is_synapse = self._is_synapse_model(model_id)
            if is_synapse:
                self.console.print(f"[{COGNICLI_ACCENT}]🧠 Detected Synapse model - loading with custom architecture[/]")
                config.model_type = "synapse"
            else:
                config.model_type = "transformers"
            
            # Get quantization config
            quant_config = self._get_quantization_config(config.precision)
            
            # Load tokenizer first
            try:
                self.current_tokenizer = AutoTokenizer.from_pretrained(
                    model_id,
                    use_fast=config.use_fast_tokenizer,
                    trust_remote_code=config.trust_remote_code
                )
                
                # Handle missing pad token
                if self.current_tokenizer.pad_token is None:
                    self.current_tokenizer.pad_token = self.current_tokenizer.eos_token
                
                # Add special tokens for Synapse models
                if is_synapse:
                    special_tokens = ['<think>', '</think>', '<answer>', '</answer>']
                    self.current_tokenizer.add_special_tokens({'additional_special_tokens': special_tokens})
                
            except Exception as e:
                self.console.print(f"[red]Failed to load tokenizer: {e}[/red]")
                return False
            
            # Load model
            try:
                # Prepare model loading arguments
                model_kwargs = {
                    "trust_remote_code": config.trust_remote_code,
                    "device_map": "auto" if config.device == "auto" else None,
                }
                
                # Apply quantization if specified
                if quant_config:
                    if quant_config.get("load_in_4bit") or quant_config.get("load_in_8bit"):
                        # Create BitsAndBytesConfig for modern quantization
                        bnb_config = BitsAndBytesConfig(
                            load_in_4bit=quant_config.get("load_in_4bit", False),
                            load_in_8bit=quant_config.get("load_in_8bit", False),
                            bnb_4bit_compute_dtype=quant_config.get("bnb_4bit_compute_dtype", torch.float16),
                            bnb_4bit_use_double_quant=quant_config.get("bnb_4bit_use_double_quant", True),
                            bnb_4bit_quant_type=quant_config.get("bnb_4bit_quant_type", "nf4")
                        )
                        model_kwargs["quantization_config"] = bnb_config
                
                # Apply dtype if specified
                if quant_config.get("torch_dtype"):
                    model_kwargs["torch_dtype"] = quant_config.get("torch_dtype")
                
                # Load the actual model specified by model_id
                self.current_model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    **model_kwargs
                )
                
                # Resize embeddings if needed (for Synapse models)
                if is_synapse and hasattr(self.current_model, 'resize_token_embeddings'):
                    self.current_model.resize_token_embeddings(len(self.current_tokenizer))
                
                # Move to GPU if available and not using device_map="auto"
                if config.device == "auto" and torch.cuda.is_available() and not model_kwargs.get("device_map"):
                    self.current_model = self.current_model.cuda()
                
                self.console.print(f"[bold green]✅ Loaded {config.model_type.title()} model:[/] {model_id}")
                if torch.cuda.is_available():
                    self.console.print(f"[dim]Device: {self.current_model.device}[/dim]")
                return True
                
            except Exception as e:
                self.console.print(f"[red]Failed to load model: {e}[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]Transformers loading error: {e}[/red]")
            return False
    
    def _download_gguf_file(self, model_id: str) -> Optional[Path]:
        """Download GGUF file with progress indication"""
        try:
            files = self.api.list_files(model_id)
            gguf_file = next((f for f in files if f.rfilename.endswith(".gguf")), None)
            
            if not gguf_file:
                self.console.print(f"[red]No GGUF file found for {model_id}[/red]")
                return None
            
            path = self.cache_dir / gguf_file.rfilename
            
            if not path.exists():
                self.console.print(f"[yellow]Downloading GGUF file: {gguf_file.rfilename} ...[/yellow]")
                try:
                    hf_hub_download(
                        repo_id=model_id, 
                        filename=gguf_file.rfilename, 
                        local_dir=self.cache_dir
                    )
                except Exception as e:
                    self.console.print(f"[red]Download failed: {e}[/red]")
                    return None
            
            return path
            
        except Exception as e:
            self.console.print(f"[red]Failed to find GGUF file: {e}[/red]")
            return None
    
    def _is_synapse_model(self, model_id: str) -> bool:
        """Check if a model is a Synapse model by examining its config"""
        try:
            config_info = self.api.model_info(model_id)
            for file_info in config_info.siblings:
                if file_info.rfilename == "config.json":
                    config_path = hf_hub_download(repo_id=model_id, filename="config.json")
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    architectures = config.get("architectures", [])
                    model_type = config.get("model_type", "")
                    auto_map = config.get("auto_map", {})
                    
                    synapse_indicators = [
                        "SynapseMultiMoEModel" in architectures,
                        model_type == "synapse",
                        "synapse" in str(auto_map).lower(),
                        "num_experts" in config,
                        any("synapse" in arch.lower() for arch in architectures)
                    ]
                    
                    return any(synapse_indicators)
        except Exception:
            pass
        return False
    
    def _get_quantization_config(self, precision: str) -> Dict[str, Any]:
        """Get quantization configuration with proper error handling"""
        config = {}
        
        if precision in ("q4", "q8"):
            if not BNB_AVAILABLE:
                self.console.print(f"[yellow]⚠️  Quantization {precision} requested but bitsandbytes not available.[/yellow]")
                self.console.print(f"[dim]Install with: pip install bitsandbytes[/dim]")
                return config
            
            if precision == "q8":
                config["load_in_8bit"] = True
                self.console.print(f"[{COGNICLI_ACCENT}]🔧 Loading model in 8-bit quantization[/{COGNICLI_ACCENT}]")
            elif precision == "q4":
                config["load_in_4bit"] = True
                config["bnb_4bit_compute_dtype"] = torch.float16
                config["bnb_4bit_use_double_quant"] = True
                config["bnb_4bit_quant_type"] = "nf4"
                self.console.print(f"[{COGNICLI_ACCENT}]🔧 Loading model in 4-bit quantization[/{COGNICLI_ACCENT}]")
        elif precision in ("fp16", "bf16"):
            dtype_map = {"fp16": torch.float16, "bf16": torch.bfloat16}
            config["torch_dtype"] = dtype_map[precision]
            self.console.print(f"[{COGNICLI_ACCENT}]🔧 Loading model with {precision} precision[/{COGNICLI_ACCENT}]")
        
        return config

class PremiumChatInterface:
    """Premium chat interface with beautiful formatting for reasoning and responses"""
    
    def __init__(self, console: Console, model_manager):
        self.console = console
        self.model_manager = model_manager
    
    def show_welcome_banner(self):
        """Show a beautiful welcome banner for chat mode"""
        config = self.model_manager.get_current_config()
        if not config:
            return
            
        welcome_content = f"""
[bold {COGNICLI_ACCENT}]🚀 Premium Chat Mode Activated![/bold {COGNICLI_ACCENT}]

[green]Model:[/green] {config.name}
[green]Type:[/green] {config.model_type.title()}
[green]Precision:[/green] {config.precision}
[green]Context Length:[/green] {config.context_length:,} tokens

[bold {COGNICLI_ACCENT}]Features:[/bold {COGNICLI_ACCENT}]
✨ Beautiful reasoning display with <think> blocks
🎯 Advanced tool use capabilities
🔄 Streaming responses with live updates
💫 Premium formatting for all interactions

[dim]Type your message to start chatting, or 'help' for commands...[/dim]
"""
        
        panel = Panel(
            welcome_content,
            title="🤖 AI Chat Interface",
            border_style=COGNICLI_ACCENT,
            padding=(1, 2),
        )
        
        self.console.print(panel)
        self.console.print()
    
    def display_thinking(self, thinking_content: str):
        """Display thinking content in a beautiful panel"""
        if not thinking_content.strip():
            return
            
        thinking_panel = Panel(
            Markdown(thinking_content),
            title="🤔 AI Reasoning Process",
            border_style="dim blue",
            title_style="dim italic",
            padding=(1, 2),
        )
        self.console.print(thinking_panel)
        self.console.print()
    
    def display_answer(self, answer_content: str):
        """Display answer content with premium formatting"""
        if not answer_content.strip():
            return
            
        # Try to render as markdown for rich formatting
        try:
            self.console.print(Markdown(answer_content))
        except Exception:
            # Fall back to plain text if markdown fails
            self.console.print(answer_content)
    
    def display_tool_execution(self, tool_name: str, result: str):
        """Display tool execution results in a premium panel"""
        tool_panel = Panel(
            result,
            title=f"🔧 Tool Executed: {tool_name}",
            border_style=COGNICLI_ACCENT,
            padding=(1, 2),
        )
        self.console.print(tool_panel)
        self.console.print()
    
    def display_response_stats(self, response_time: float, token_count: Optional[int] = None):
        """Display response statistics"""
        stats_text = f"⏱️  Response time: {response_time:.2f}s"
        if token_count:
            tokens_per_sec = token_count / response_time if response_time > 0 else 0
            stats_text += f" | 🔤 Tokens: {token_count} ({tokens_per_sec:.1f} tokens/sec)"
        
        self.console.print(f"[dim]{stats_text}[/dim]")
        self.console.print()

class ResponseGenerator:
    """Enhanced response generation with beautiful chat interface"""
    
    def __init__(self, model_manager, console: Console):
        self.model_manager = model_manager
        self.console = console
        self.chat_interface = PremiumChatInterface(console, model_manager)
        self.system_tool_prompt = self._get_system_tool_prompt()
        self.synapse_system_prompt = self._get_synapse_system_prompt()
    
    def _get_system_tool_prompt(self) -> str:
        return """You are CogniCLI, a helpful AI assistant and code agent with tool use.

Available tools:
- write_file(filepath, content): Write the given content to the file at 'filepath'.
- append_file(filepath, content): Append the content to a file.
- read_file(filepath): Read and return content of the file.
- list_dir(path="."): List files in a directory.
- run_shell(cmd): Run the shell command and return output.
- python_eval(code): Run Python code and return output.
- pip_install(package): Pip install a package by name.

If you want to use a tool, respond ONLY with a JSON object of this form:
{"tool_call": "<tool_name>", "args": {"arg1": "value1", ...}}
Otherwise, reply as normal.

Examples:
{"tool_call": "write_file", "args": {"filepath": "main.py", "content": "print('hi')"}}
{"tool_call": "append_file", "args": {"filepath": "main.py", "content": "print('hi again')"}}
{"tool_call": "read_file", "args": {"filepath": "main.py"}}
{"tool_call": "list_dir", "args": {"path": "."}}
{"tool_call": "run_shell", "args": {"cmd": "ls -la"}}
{"tool_call": "python_eval", "args": {"code": "print(1+1)"}}
{"tool_call": "pip_install", "args": {"package": "requests"}}"""

    def _get_synapse_system_prompt(self) -> str:
        return """You are Synapse, a helpful AI assistant with advanced reasoning capabilities. You use a think-answer structure when appropriate.

When solving complex problems:
1. Use <think> tags to show your step-by-step reasoning
2. Use <answer> tags to provide your final response

Available tools:
- write_file(filepath, content): Write content to a file
- append_file(filepath, content): Append content to a file
- read_file(filepath): Read file content
- list_dir(path="."): List directory contents
- run_shell(cmd): Execute shell commands
- python_eval(code): Execute Python code
- pip_install(package): Install Python packages

To use tools, respond with JSON: {"tool_call": "<tool_name>", "args": {"arg1": "value1", ...}}

Examples:
{"tool_call": "write_file", "args": {"filepath": "test.py", "content": "print('Hello')"}}
{"tool_call": "python_eval", "args": {"code": "print(2 + 2)"}}"""

    def generate_response(self, prompt: str, stream: bool = True, show_thinking: bool = True) -> str:
        """Generate response with premium chat interface"""
        if not self.model_manager.is_model_loaded():
            self.console.print(f"[{COGNICLI_ACCENT}]No model loaded. Use --model to load a model.[/{COGNICLI_ACCENT}]")
            return ""

        config = self.model_manager.get_current_config()
        if not config:
            self.console.print("[red]Model configuration not found.[/red]")
            return ""

        try:
            # Handle different model types
            if config.model_type == "gguf":
                response = self._generate_gguf(prompt, config)
            elif config.model_type == "synapse":
                response = self._generate_synapse(prompt, config, show_thinking)
            else:
                response = self._generate_transformers(prompt, config)

            # Handle tool calls
            tool_call = self._extract_tool_call(response)
            if tool_call:
                self._process_tool_call(tool_call)
            else:
                # Display response with premium formatting
                if config.model_type == "synapse" and show_thinking:
                    self._display_synapse_response_premium(response)
                else:
                    self.chat_interface.display_answer(response)

            return response

        except Exception as e:
            self.console.print(f"[red]Generation error: {e}[/red]")
            return ""

    def _generate_gguf(self, prompt: str, config: ModelConfig) -> str:
        """Generate response for GGUF models"""
        try:
            full_prompt = self.system_tool_prompt + "\n\nUser: " + prompt + "\nAssistant:"
            response = self.model_manager.current_model(
                prompt=full_prompt, 
                max_tokens=config.max_tokens, 
                temperature=config.temperature,
                top_p=config.top_p,
                stop=["User:", "\n\n"]
            )
            return response['choices'][0]['text'].strip()
        except Exception as e:
            self.console.print(f"[red]GGUF generation error: {e}[/red]")
            return ""

    def _generate_synapse(self, prompt: str, config: ModelConfig, show_thinking: bool = True) -> str:
        """Generate response for Synapse models with proper formatting"""
        try:
            system_prompt = self.synapse_system_prompt
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"

            inputs = self.model_manager.current_tokenizer(full_prompt, return_tensors="pt")
            input_ids = inputs["input_ids"].to(self.model_manager.current_model.device)
            attention_mask = inputs.get("attention_mask", None)

            gen_args = {
                "input_ids": input_ids,
                "max_new_tokens": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "do_sample": True,
                "eos_token_id": self.model_manager.current_tokenizer.eos_token_id,
                "pad_token_id": self.model_manager.current_tokenizer.eos_token_id,
                "repetition_penalty": 1.1,
            }

            if attention_mask is not None:
                gen_args["attention_mask"] = attention_mask.to(self.model_manager.current_model.device)

            with torch.no_grad():
                outputs = self.model_manager.current_model.generate(**gen_args)

            response = self.model_manager.current_tokenizer.decode(
                outputs[0][input_ids.shape[1]:],
                skip_special_tokens=True
            )

            return response.strip()

        except Exception as e:
            self.console.print(f"[red]Synapse generation error: {e}[/red]")
            return ""

    def _generate_transformers(self, prompt: str, config: ModelConfig) -> str:
        """Generate response for Transformers models"""
        try:
            full_prompt = self.system_tool_prompt + "\n\nUser: " + prompt + "\nAssistant:"
            
            inputs = self.model_manager.current_tokenizer(full_prompt, return_tensors="pt")
            input_ids = inputs["input_ids"].to(self.model_manager.current_model.device)
            attention_mask = inputs.get("attention_mask", None)
            
            gen_args = {
                "input_ids": input_ids,
                "max_new_tokens": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "do_sample": True,
                "eos_token_id": self.model_manager.current_tokenizer.eos_token_id,
                "pad_token_id": self.model_manager.current_tokenizer.eos_token_id,
            }
            
            if attention_mask is not None:
                gen_args["attention_mask"] = attention_mask.to(self.model_manager.current_model.device)
            
            with torch.no_grad():
                outputs = self.model_manager.current_model.generate(**gen_args)
            
            response = self.model_manager.current_tokenizer.decode(
                outputs[0][input_ids.shape[1]:], 
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            self.console.print(f"[red]Transformers generation error: {e}[/red]")
            return ""

    def _extract_tool_call(self, response: str) -> Optional[Dict]:
        """Extract tool calls from response with improved regex"""
        import re
        
        # Try to find JSON tool calls
        json_pattern = r'\{[^{}]*"tool_call"\s*:\s*"[^"]+"[^{}]*\}'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        for match in matches:
            try:
                obj = json.loads(match)
                if "tool_call" in obj and "args" in obj:
                    return obj
            except json.JSONDecodeError:
                continue
        
        # Try parsing the entire response as JSON
        try:
            obj = json.loads(response.strip())
            if "tool_call" in obj and "args" in obj:
                return obj
        except json.JSONDecodeError:
            pass
        
        return None

    def _process_tool_call(self, tool_call: Dict):
        """Process tool calls with premium interface"""
        tool_name = tool_call.get("tool_call", "")
        args = tool_call.get("args", {})
        
        if tool_name in TOOLS:
            try:
                result = TOOLS[tool_name](**args)
                self.chat_interface.display_tool_execution(tool_name, result)
            except Exception as e:
                error_result = f"❌ Error running tool '{tool_name}': {e}"
                self.chat_interface.display_tool_execution(tool_name, error_result)
        else:
            error_result = f"❌ Unknown tool '{tool_name}'"
            self.chat_interface.display_tool_execution("Tool Error", error_result)

    def _display_synapse_response_premium(self, response: str):
        """Display Synapse model response with premium formatting for thinking tags"""
        import re

        # Extract thinking and answer sections
        think_pattern = r'<think>(.*?)</think>'
        answer_pattern = r'<answer>(.*?)</answer>'

        think_matches = re.findall(think_pattern, response, re.DOTALL)
        answer_matches = re.findall(answer_pattern, response, re.DOTALL)

        # Display thinking section if present
        if think_matches:
            thinking_content = think_matches[0].strip()
            if thinking_content:
                self.chat_interface.display_thinking(thinking_content)

        # Display answer section if present
        if answer_matches:
            answer_content = answer_matches[0].strip()
            if answer_content:
                self.chat_interface.display_answer(answer_content)
        else:
            # If no structured format, just display the whole response
            # but remove any remaining think tags
            cleaned_response = re.sub(r'</?(?:think|answer)>', '', response).strip()
            if cleaned_response:
                self.chat_interface.display_answer(cleaned_response)

# Tool functions
def write_file(filepath: str, content: str) -> str:
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Wrote to {filepath}"
    except Exception as e:
        return f"❌ Error writing file: {e}"

def read_file(filepath: str) -> str:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"❌ Error reading file: {e}"

def run_shell(cmd: str) -> str:
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        return f"$ {cmd}\n{result.stdout}{result.stderr}"
    except Exception as e:
        return f"❌ Error running shell command: {e}"

def list_dir(path: str = ".") -> str:
    try:
        files = os.listdir(path)
        return f"Files in {os.path.abspath(path)}:\n" + "\n".join(files)
    except Exception as e:
        return f"❌ Error listing directory: {e}"

def append_file(filepath: str, content: str) -> str:
    try:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Appended to {filepath}"
    except Exception as e:
        return f"❌ Error appending file: {e}"

def python_eval(code: str) -> str:
    import io
    import contextlib
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(code, {}, {})
        return f"Python output:\n{buf.getvalue()}"
    except Exception as e:
        return f"❌ Python error: {e}"

def pip_install(package: str) -> str:
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        return f"✅ Installed package {package}"
    except Exception as e:
        return f"❌ Pip install error: {e}"

TOOLS = {
    "write_file": write_file,
    "read_file": read_file,
    "run_shell": run_shell,
    "list_dir": list_dir,
    "append_file": append_file,
    "python_eval": python_eval,
    "pip_install": pip_install,
}

class OllamaManager:
    """Manage Ollama operations including listing, pulling, and searching models"""
    
    def __init__(self, console: Console):
        self.console = console
        self.base_url = "http://localhost:11434"
        self.available_quantizations = [
            "q4_0", "q4_1", "q4_K_M", "q4_K_S", "q5_0", "q5_1", "q5_K_M", "q5_K_S",
            "q8_0", "f16", "f32"
        ]
    
    def is_ollama_running(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all available Ollama models"""
        try:
            if not self.is_ollama_running():
                self.console.print("[red]❌ Ollama service is not running. Start Ollama first.[/red]")
                return []
            
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("models", []):
                    model_info = {
                        "name": model.get("name", "Unknown"),
                        "size": model.get("size", 0),
                        "modified_at": model.get("modified_at", "Unknown"),
                        "digest": model.get("digest", "Unknown")[:8] if model.get("digest") else "Unknown"
                    }
                    models.append(model_info)
                return models
            else:
                self.console.print(f"[red]Failed to list Ollama models: {response.status_code}[/red]")
                return []
        except Exception as e:
            self.console.print(f"[red]Error listing Ollama models: {e}[/red]")
            return []
    
    def search_models(self, query: str) -> List[Dict[str, Any]]:
        """Search for Ollama models"""
        try:
            if not self.is_ollama_running():
                self.console.print("[red]❌ Ollama service is not running. Start Ollama first.[/red]")
                return []
            
            # Use Ollama's search API
            response = requests.get(f"{self.base_url}/api/search", params={"q": query}, timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("models", []):
                    model_info = {
                        "name": model.get("name", "Unknown"),
                        "description": model.get("description", "No description"),
                        "downloads": model.get("downloads", 0),
                        "likes": model.get("likes", 0),
                        "tags": model.get("tags", []),
                        "size": model.get("size", 0)
                    }
                    models.append(model_info)
                return models
            else:
                self.console.print(f"[red]Failed to search Ollama models: {response.status_code}[/red]")
                return []
        except Exception as e:
            self.console.print(f"[red]Error searching Ollama models: {e}[/red]")
            return []
    
    def pull_model(self, model_name: str, quantization: str = None) -> bool:
        """Pull a model from Ollama"""
        try:
            if not self.is_ollama_running():
                self.console.print("[red]❌ Ollama service is not running. Start Ollama first.[/red]")
                return False
            
            # If quantization is specified, append it to model name
            if quantization:
                full_model_name = f"{model_name}:{quantization}"
            else:
                full_model_name = model_name
            
            self.console.print(f"[{COGNICLI_ACCENT}]Pulling Ollama model: {full_model_name}[/{COGNICLI_ACCENT}]")
            
            # Start pull request
            response = requests.post(f"{self.base_url}/api/pull", json={"name": full_model_name}, timeout=30)
            if response.status_code == 200:
                self.console.print(f"[bold green]✅ Successfully pulled {full_model_name}[/bold green]")
                return True
            else:
                self.console.print(f"[red]❌ Failed to pull {full_model_name}: {response.status_code}[/red]")
                return False
        except Exception as e:
            self.console.print(f"[red]Error pulling Ollama model: {e}[/red]")
            return False
    
    def get_available_quantizations(self) -> List[str]:
        """Get list of available quantization options"""
        return self.available_quantizations.copy()
    
    def show_quantization_help(self):
        """Show help for quantization options"""
        help_text = f"""
[bold {COGNICLI_ACCENT}]Available GGUF Quantizations:[/bold {COGNICLI_ACCENT}]

[green]4-bit Quantizations:[/green]
• [cyan]q4_0[/cyan] - Standard 4-bit quantization (balanced)
• [cyan]q4_1[/cyan] - Improved 4-bit quantization
• [cyan]q4_K_M[/cyan] - 4-bit K-quants with medium quality
• [cyan]q4_K_S[/cyan] - 4-bit K-quants with small size

[green]5-bit Quantizations:[/green]
• [cyan]q5_0[/cyan] - Standard 5-bit quantization
• [cyan]q5_1[/cyan] - Improved 5-bit quantization
• [cyan]q5_K_M[/cyan] - 5-bit K-quants with medium quality
• [cyan]q5_K_S[/cyan] - 5-bit K-quants with small size

[green]8-bit and Full Precision:[/green]
• [cyan]q8_0[/cyan] - 8-bit quantization (high quality)
• [cyan]f16[/cyan] - Half precision (16-bit)
• [cyan]f32[/cyan] - Full precision (32-bit)

[dim]Usage Examples:[/dim]
• [yellow]--ollama pull llama2:q4_K_M[/yellow] - Pull 4-bit K-quants version
• [yellow]--ollama pull codellama:q8_0[/yellow] - Pull 8-bit version
• [yellow]--model path/to/model.gguf --quantization q4_K_M[/yellow] - Load specific quantization
"""
        self.console.print(Panel(help_text, title="🔧 Quantization Guide", border_style=COGNICLI_ACCENT))

class CogniCLI:
    """Enhanced CogniCLI with premium features and automatic chat mode"""
    
    def __init__(self):
        self.console = Console()
        self.model_manager = ModelManager(self.console)
        self.response_generator = ResponseGenerator(self.model_manager, self.console)
        self.ollama_manager = OllamaManager(self.console)
        
        try:
            # Add timeout to prevent hanging
            import os
            os.environ['HF_HUB_DOWNLOAD_TIMEOUT'] = '30'
            os.environ['HF_HUB_OFFLINE'] = '0'
            self.api = HfApi()
        except Exception as e:
            print(f"Warning: Could not initialize HuggingFace API: {e}")
            self.api = None
            
        try:
            self.cache_dir = Path.home() / '.cognicli'
            self.cache_dir.mkdir(exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create cache directory: {e}")
            self.cache_dir = Path.cwd() / '.cognicli'
            try:
                self.cache_dir.mkdir(exist_ok=True)
            except Exception as e2:
                print(f"Warning: Could not create fallback cache directory: {e2}")
                self.cache_dir = None
        
        # Set up signal handlers for graceful shutdown
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except Exception as e:
            print(f"Warning: Could not set up signal handlers: {e}")
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.console.print(f"\n[yellow]Received signal {signum}, shutting down gracefully...[/yellow]")
        if self.model_manager.is_model_loaded():
            self.model_manager.unload_current_model()
        sys.exit(0)

    def show_logo(self):
        """Display the enhanced logo with better formatting"""
        logo_text = Text(LOGO)
        logo_text.stylize(f"bold {COGNICLI_ACCENT}")
        
        # Add version and status info
        version_text = Text("v2.2.4 - Premium Edition", style="dim")
        status_text = Text("🚀 Enhanced • Robust • Premium", style="green")
        
        panel = Panel(
            Align.center(logo_text),
            title="CogniCLI",
            subtitle="Premium AI Command Line Interface",
            border_style=COGNICLI_ACCENT,
            padding=(1, 4),
        )
        
        self.console.print(Align.center(panel))
        self.console.print(Align.center(version_text))
        self.console.print(Align.center(status_text))
        self.console.print()

    def load_model(self, model_id: str, **kwargs) -> bool:
        """Load a model and automatically transition to premium chat mode"""
        try:
            # Show loading status
            with self.console.status(f"[{COGNICLI_ACCENT}]Loading {model_id}...[/{COGNICLI_ACCENT}]", spinner="dots"):
                success = self.model_manager.load_model(model_id, **kwargs)
            
            if success:
                config = self.model_manager.get_current_config()
                if config:
                    self.console.print(f"[bold green]✅ Model loaded successfully![/bold green]")
                    self.console.print(f"[dim]Type: {config.model_type.title()}[/dim]")
                    self.console.print(f"[dim]Precision: {config.precision}[/dim]")
                    if torch.cuda.is_available():
                        self.console.print(f"[dim]GPU: Available[/dim]")
                    else:
                        self.console.print(f"[dim]GPU: Not available[/dim]")
                    
                    # Automatically start premium chat mode
                    self.console.print(f"\n[bold {COGNICLI_ACCENT}]🎯 Automatically entering Premium Chat Mode...[/bold {COGNICLI_ACCENT}]")
                    time.sleep(1)  # Brief pause for better UX
                    self.start_premium_chat_mode()
                    
                return True
            else:
                self.console.print(f"[red]❌ Failed to load model {model_id}[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[red]❌ Error loading model: {e}[/red]")
            return False

    def start_premium_chat_mode(self):
        """Start the premium chat mode with beautiful interface"""
        if not self.model_manager.is_model_loaded():
            self.console.print(f"[red]No model loaded. Use --model to load a model first.[/red]")
            return
        
        # Show welcome banner
        self.response_generator.chat_interface.show_welcome_banner()
        
        chat_history = []
        
        while True:
            try:
                # Get user input with premium prompt
                prompt = Prompt.ask(
                    f"[bold {COGNICLI_ACCENT}]You[/bold {COGNICLI_ACCENT}] [dim]❯[/dim]",
                    default="",
                    show_default=False
                )
                
                if not prompt.strip():
                    continue
                    
                # Handle special commands
                if prompt.lower() in ["exit", "quit", "q", "/exit", "/quit"]:
                    self.console.print(f"\n[bold yellow]👋 Goodbye from CogniCLI! Thanks for using Premium Chat Mode![/bold yellow]")
                    break
                    
                elif prompt.lower() in ["help", "?", "/help"]:
                    self.show_chat_help()
                    continue
                    
                elif prompt.lower() in ["config", "/config"]:
                    self.show_current_config()
                    continue
                    
                elif prompt.lower() in ["benchmark", "/benchmark"]:
                    self.console.print(f"[{COGNICLI_ACCENT}]Running quick benchmark...[/{COGNICLI_ACCENT}]")
                    self.benchmark_model()
                    continue
                    
                elif prompt.lower() in ["clear", "/clear"]:
                    chat_history.clear()
                    self.console.print("[green]✨ Chat history cleared.[/green]")
                    continue
                    
                elif prompt.lower() in ["status", "/status"]:
                    self.show_model_status()
                    continue
                
                # Show generation indicator
                self.console.print(f"\n[dim]🤖 {self.model_manager.get_current_config().name} is thinking...[/dim]")
                
                # Generate response with timing
                start_time = time.time()
                response = self.response_generator.generate_response(prompt, stream=True, show_thinking=True)
                end_time = time.time()
                
                if response:
                    # Add to chat history
                    chat_history.append({
                        "user": prompt,
                        "assistant": response,
                        "timestamp": datetime.now(),
                        "response_time": end_time - start_time
                    })
                    
                    # Show response stats with premium formatting
                    response_time = end_time - start_time
                    # Estimate token count (rough approximation)
                    estimated_tokens = len(response.split())
                    self.response_generator.chat_interface.display_response_stats(response_time, estimated_tokens)
                    
            except KeyboardInterrupt:
                self.console.print(f"\n[bold yellow]⏸️  Chat paused. Type 'exit' to quit or continue chatting.[/bold yellow]")
            except Exception as e:
                self.console.print(f"[red]❌ Error: {e}[/red]")

    def show_chat_help(self):
        """Show help for premium chat mode"""
        help_text = f"""
[bold {COGNICLI_ACCENT}]Premium Chat Mode Commands:[/bold {COGNICLI_ACCENT}]

[green]💬 Chat Commands:[/green]
• Simply type your message to chat with the AI
• The AI will show reasoning with <think> blocks for complex questions
• Tool calls are automatically detected and executed

[green]🔧 Special Commands:[/green]
• [cyan]/help[/cyan] or [cyan]help[/cyan] - Show this help message
• [cyan]/config[/cyan] or [cyan]config[/cyan] - Show current model configuration
• [cyan]/benchmark[/cyan] or [cyan]benchmark[/cyan] - Run quick performance benchmark
• [cyan]/status[/cyan] or [cyan]status[/cyan] - Show model and system status
• [cyan]/clear[/cyan] or [cyan]clear[/cyan] - Clear chat history
• [cyan]/exit[/cyan], [cyan]/quit[/cyan], [cyan]exit[/cyan], or [cyan]quit[/cyan] - Exit chat mode

[green]✨ Premium Features:[/green]
• Beautiful reasoning display with thinking blocks
• Advanced tool execution with premium panels
• Live response timing and token statistics
• Markdown rendering for rich text responses
• Automatic model type detection and optimization

[dim]💡 Pro Tips:[/dim]
[dim]• Use Ctrl+C to pause long responses[/dim]
[dim]• Complex questions will show AI reasoning process[/dim]
[dim]• All file operations and code execution are supported[/dim]
"""
        self.console.print(Panel(help_text, title="📚 Premium Chat Help", border_style=COGNICLI_ACCENT))

    def show_current_config(self):
        """Show current model configuration with premium formatting"""
        if not self.model_manager.is_model_loaded():
            self.console.print("[yellow]No model loaded.[/yellow]")
            return
        
        config = self.model_manager.get_current_config()
        if not config:
            self.console.print("[red]Model configuration not found.[/red]")
            return
        
        # Create a beautiful configuration display
        config_table = Table(
            title="Current Model Configuration",
            box=box.ROUNDED,
            title_style=COGNICLI_ACCENT
        )
        config_table.add_column("Setting", style=COGNICLI_ACCENT)
        config_table.add_column("Value", style="green")
        
        config_table.add_row("Model Name", config.name)
        config_table.add_row("Model Type", config.model_type.title())
        config_table.add_row("Precision", config.precision)
        config_table.add_row("Context Length", f"{config.context_length:,} tokens")
        config_table.add_row("Temperature", str(config.temperature))
        config_table.add_row("Top P", str(config.top_p))
        config_table.add_row("Max Tokens", str(config.max_tokens))
        config_table.add_row("Device", config.device)
        
        if config.last_used:
            config_table.add_row("Last Used", config.last_used.strftime('%Y-%m-%d %H:%M:%S'))
        
        self.console.print(config_table)

    def show_model_status(self):
        """Show current model and system status with premium formatting"""
        status_table = Table(
            title="System & Model Status",
            box=box.ROUNDED,
            title_style=COGNICLI_ACCENT
        )
        status_table.add_column("Component", style=COGNICLI_ACCENT)
        status_table.add_column("Status", style="green")
        status_table.add_column("Details", style="cyan")
        
        # System status
        status_table.add_row(
            "Model Loaded", 
            "✅ Yes" if self.model_manager.is_model_loaded() else "❌ No",
            self.model_manager.current_model_id or "None"
        )
        
        status_table.add_row(
            "GPU Available", 
            "✅ Yes" if torch.cuda.is_available() else "❌ No",
            f"CUDA {torch.version.cuda}" if torch.cuda.is_available() else "CPU Only"
        )
        
        status_table.add_row(
            "Memory Usage", 
            f"{psutil.virtual_memory().percent}%",
            f"{psutil.virtual_memory().used // (1024**3)} GB / {psutil.virtual_memory().total // (1024**3)} GB"
        )
        
        status_table.add_row(
            "Python Version", 
            sys.version.split()[0],
            f"Platform: {sys.platform}"
        )
        
        # Model specific status
        if self.model_manager.is_model_loaded():
            config = self.model_manager.get_current_config()
            if config:
                status_table.add_row(
                    "Model Type", 
                    config.model_type.title(),
                    f"Precision: {config.precision}"
                )
                
                if torch.cuda.is_available() and hasattr(self.model_manager.current_model, 'device'):
                    status_table.add_row(
                        "Model Device", 
                        str(self.model_manager.current_model.device),
                        "GPU Accelerated"
                    )
        
        self.console.print(status_table)

    def benchmark_model(self) -> Dict[str, Any]:
        """Enhanced benchmark with comprehensive metrics"""
        if not self.model_manager.is_model_loaded():
            self.console.print("[red]No model loaded.[/red]")
            return {}
        
        try:
            config = self.model_manager.get_current_config()
            if not config:
                self.console.print("[red]Model configuration not found.[/red]")
                return {}
            
            self.console.print(f"[{COGNICLI_ACCENT}]Running benchmark on {config.name}...[/{COGNICLI_ACCENT}]")
            
            # Test prompts for different scenarios
            test_prompts = [
                "The quick brown fox jumps over the lazy dog.",
                "Python is a programming language that emphasizes code readability.",
                "Machine learning algorithms can process vast amounts of data efficiently."
            ]
            
            results = {
                "model": config.name,
                "type": config.model_type,
                "precision": config.precision,
                "runs": 3,  # Reduced for faster testing
                "prompts": len(test_prompts),
                "total_tokens": 0,
                "total_time": 0,
                "prompt_results": []
            }
            
            for i, prompt in enumerate(test_prompts):
                self.console.print(f"[dim]Testing prompt {i+1}/{len(test_prompts)}: {prompt[:30]}...[/dim]")
                
                prompt_times = []
                prompt_tokens = 0
                
                for run in range(results["runs"]):
                    start_time = time.time()
                    
                    try:
                        if config.model_type == "gguf":
                            response = self.model_manager.current_model(
                                prompt=prompt, 
                                max_tokens=32, 
                                temperature=0.1
                            )
                            tokens = len(response['choices'][0]['text'].split())
                        else:
                            inputs = self.model_manager.current_tokenizer(prompt, return_tensors="pt")
                            input_ids = inputs["input_ids"].to(self.model_manager.current_model.device)
                            
                            with torch.no_grad():
                                outputs = self.model_manager.current_model.generate(
                                    input_ids=input_ids, 
                                    max_new_tokens=32,
                                    temperature=0.1
                                )
                            
                            response_text = self.model_manager.current_tokenizer.decode(
                                outputs[0][input_ids.shape[1]:], 
                                skip_special_tokens=True
                            )
                            tokens = len(response_text.split())
                        
                        end_time = time.time()
                        prompt_times.append(end_time - start_time)
                        prompt_tokens += tokens
                        
                    except Exception as e:
                        self.console.print(f"[red]Benchmark run {run+1} failed: {e}[/red]")
                        continue
                
                if prompt_times:
                    avg_time = np.mean(prompt_times)
                    std_time = np.std(prompt_times)
                    tokens_per_sec = prompt_tokens / avg_time if avg_time > 0 else 0
                    
                    results["prompt_results"].append({
                        "prompt": prompt,
                        "avg_time": avg_time,
                        "std_time": std_time,
                        "tokens_per_sec": tokens_per_sec,
                        "total_tokens": prompt_tokens
                    })
                    
                    results["total_time"] += avg_time * results["runs"]
                    results["total_tokens"] += prompt_tokens
            
            # Calculate overall metrics
            if results["prompt_results"]:
                overall_tokens_per_sec = results["total_tokens"] / results["total_time"] if results["total_time"] > 0 else 0
                results["overall_tokens_per_sec"] = overall_tokens_per_sec
                
                # Display results
                self.display_benchmark_results(results)
            
            return results
            
        except Exception as e:
            self.console.print(f"[red]Benchmark failed: {e}[/red]")
            return {}

    def display_benchmark_results(self, results: Dict[str, Any]):
        """Display benchmark results in a beautiful table"""
        # Overall results
        overall_table = Table(
            title="🏁 Overall Benchmark Results", 
            box=box.ROUNDED, 
            title_style=COGNICLI_ACCENT
        )
        overall_table.add_column("Metric", style=COGNICLI_ACCENT)
        overall_table.add_column("Value", style="green")
        
        overall_table.add_row("Model", results["model"])
        overall_table.add_row("Type", results["type"].title())
        overall_table.add_row("Precision", results["precision"])
        overall_table.add_row("Total Tokens", f"{results['total_tokens']:,}")
        overall_table.add_row("Total Time", f"{results['total_time']:.3f}s")
        overall_table.add_row("Overall Speed", f"{results.get('overall_tokens_per_sec', 0):.2f} tokens/sec")
        
        self.console.print(overall_table)
        self.console.print()
        
        # Detailed results by prompt
        if results["prompt_results"]:
            detail_table = Table(
                title="📊 Detailed Results by Prompt", 
                box=box.ROUNDED, 
                title_style=COGNICLI_ACCENT
            )
            detail_table.add_column("Prompt", style=COGNICLI_ACCENT, no_wrap=True)
            detail_table.add_column("Avg Time (s)", style="green")
            detail_table.add_column("Tokens/sec", style="cyan")
            detail_table.add_column("Total Tokens", style="magenta")
            
            for prompt_result in results["prompt_results"]:
                detail_table.add_row(
                    prompt_result["prompt"][:40] + "..." if len(prompt_result["prompt"]) > 40 else prompt_result["prompt"],
                    f"{prompt_result['avg_time']:.3f}",
                    f"{prompt_result['tokens_per_sec']:.2f}",
                    str(prompt_result['total_tokens'])
                )
            
            self.console.print(detail_table)

    def list_models(self, filter_term: str = "") -> List[dict]:
        """List models with enhanced filtering and display"""
        try:
            with self.console.status(f"[{COGNICLI_ACCENT}]Searching models...[/{COGNICLI_ACCENT}]"):
                models = self.api.list_models(filter="text-generation")
            
            out = []
            for model in models:
                if filter_term.lower() in model.modelId.lower():
                    info = {
                        "id": model.modelId,
                        "downloads": getattr(model, "downloads", 0),
                        "likes": getattr(model, "likes", 0),
                        "tags": getattr(model, "tags", []),
                        "last_modified": getattr(model, "lastModified", None),
                    }
                    out.append(info)
            
            return sorted(out, key=lambda x: x['downloads'], reverse=True)
            
        except Exception as e:
            self.console.print(f"[red]Failed to list models: {e}[/red]")
            return []

    def search_models(self, query: str, limit: int = 20) -> List[dict]:
        """Search for models on Hugging Face with enhanced filtering and display"""
        try:
            with self.console.status(f"[{COGNICLI_ACCENT}]Searching for '{query}'...[/{COGNICLI_ACCENT}]"):
                # Search for models with the query
                models = self.api.list_models(
                    filter="text-generation",
                    search=query,
                    limit=limit * 2  # Get more to filter better
                )
            
            out = []
            for model in models:
                # Enhanced filtering based on query
                query_terms = query.lower().split()
                model_id_lower = model.modelId.lower()
                
                # Check if all query terms are present in model ID
                if all(term in model_id_lower for term in query_terms):
                    info = {
                        "id": model.modelId,
                        "downloads": getattr(model, "downloads", 0),
                        "likes": getattr(model, "likes", 0),
                        "tags": getattr(model, "tags", []),
                        "last_modified": getattr(model, "lastModified", None),
                        "author": getattr(model, "author", "Unknown"),
                    }
                    out.append(info)
            
            # Sort by downloads and limit results
            return sorted(out, key=lambda x: x['downloads'], reverse=True)[:limit]
            
        except Exception as e:
            self.console.print(f"[red]Failed to search models: {e}[/red]")
            return []

    def show_model_info(self, model_id: str):
        """Show detailed model information with enhanced display"""
        try:
            with self.console.status(f"[{COGNICLI_ACCENT}]Fetching model info...[/{COGNICLI_ACCENT}]"):
                info = self.api.model_info(model_id)
            
            # Create a comprehensive info panel
            info_content = f"""
[bold]{info.modelId}[/bold]

[dim]📊 Statistics:[/dim]
• [green]Downloads:[/green] {info.downloads:,}
• [yellow]Likes:[/yellow] {info.likes:,}
• [blue]Tags:[/blue] {', '.join(info.tags[:10])}{'...' if len(info.tags) > 10 else ''}

[dim]📄 Description:[/dim]
{info.cardData.get('summary', 'No summary available.')}

[dim]🔧 Model Details:[/dim]
• [cyan]Author:[/cyan] {info.author or 'Unknown'}
• [cyan]License:[/cyan] {info.license or 'Unknown'}
"""
            
            panel = Panel(
                info_content,
                title=f"Model Information: {model_id}",
                border_style=COGNICLI_ACCENT,
                padding=(1, 2),
            )
            self.console.print(panel)
            
        except Exception as e:
            self.console.print(f"[red]Failed to get info for model: {e}[/red]")

    def _format_size(self, nbytes: int) -> str:
        """Format file size with proper units"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if nbytes < 1024:
                return f"{nbytes:.1f} {unit}"
            nbytes /= 1024
        return f"{nbytes:.1f} TB"

# Main CLI class and argument parsing
def main():
    parser = argparse.ArgumentParser(
        description="CogniCLI - Premium AI Command Line Interface with Auto-Chat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cognicli --model gpt2                    # Load GPT-2 and start premium chat
  cognicli --model microsoft/DialoGPT-medium --type q4  # Load with quantization
  cognicli --search llama2                 # Search for llama2 models
  cognicli --info microsoft/DialoGPT-medium # Show model info
  cognicli --model gpt2 --benchmark       # Load model and run benchmark
  cognicli --ollama list                   # List available Ollama models
  cognicli --ollama pull llama2:q4_K_M     # Pull specific quantization
        """
    )
    
    # Model management
    parser.add_argument('--model', type=str, help='Model to load and start premium chat (Hugging Face model ID)')
    parser.add_argument('--type', choices=['bf16', 'fp16', 'fp32', 'q4', 'q8'], default='auto', 
                       help='Model precision for Transformers models (default: auto)')
    parser.add_argument('--gguf-file', type=str, help='Specific GGUF file to use')
    parser.add_argument('--context', type=int, default=2048, help='Context length (default: 2048)')
    
    # Generation parameters
    parser.add_argument('--no-think', action='store_true', help='Disable reasoning traces')
    parser.add_argument('--temperature', type=float, default=0.7, help='Sampling temperature (default: 0.7)')
    parser.add_argument('--max-tokens', type=int, default=512, help='Maximum tokens to generate (default: 512)')
    parser.add_argument('--top-p', type=float, default=0.95, help='Top-p sampling (default: 0.95)')
    
    # Analysis and benchmarking
    parser.add_argument('--benchmark', action='store_true', help='Run model benchmark after loading')
    parser.add_argument('--generate', type=str, help='Generate single response and exit')
    
    # Model exploration (non-chat modes)
    parser.add_argument('--list', type=str, nargs='?', const='', help='List models (optional filter)')
    parser.add_argument('--info', type=str, help='Show detailed model info')
    parser.add_argument('--search', type=str, help='Search for models on Hugging Face')
    
    # Ollama integration
    ollama_group = parser.add_argument_group('Ollama Operations')
    ollama_group.add_argument('--ollama', nargs='+', metavar='OPERATION',
                             help='Ollama operations: list, search <query>, pull <model>[:<quantization>], quantizations')
    
    # Output and configuration
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--version', action='version', version='CogniCLI v2.2.4 - Premium Edition')
    
    args = parser.parse_args()

    # Initialize CLI
    cli = CogniCLI()
    
    # Handle exploration commands first (these don't start chat mode)
    if args.list is not None:
        cli.show_logo()
        models = cli.list_models(args.list)
        if args.json:
            print(json.dumps(models, indent=2, default=str))
        else:
            table = Table(
                title="Available Models", 
                box=box.ROUNDED, 
                title_style=COGNICLI_ACCENT
            )
            table.add_column("Model ID", style=COGNICLI_ACCENT, no_wrap=True)
            table.add_column("Downloads", style="green", justify="right")
            table.add_column("Likes", style="yellow", justify="right")
            table.add_column("Tags", style="blue")
            
            for model in models[:20]:  # Show top 20 models
                tags = ", ".join(model['tags'][:2]) if model['tags'] else "N/A"
                table.add_row(
                    model['id'], 
                    f"{model['downloads']:,}", 
                    f"{model['likes']:,}", 
                    tags
                )
            cli.console.print(table)
        return

    if args.info:
        cli.show_logo()
        cli.show_model_info(args.info)
        return

    if args.search:
        cli.show_logo()
        models = cli.search_models(args.search, limit=20)
        if args.json:
            print(json.dumps(models, indent=2, default=str))
        else:
            table = Table(
                title=f"🔍 Search Results for '{args.search}'", 
                box=box.ROUNDED, 
                title_style=COGNICLI_ACCENT
            )
            table.add_column("Model ID", style=COGNICLI_ACCENT, no_wrap=True)
            table.add_column("Downloads", style="green", justify="right")
            table.add_column("Likes", style="yellow", justify="right")
            table.add_column("Author", style="cyan")
            
            for model in models:
                table.add_row(
                    model['id'], 
                    f"{model['downloads']:,}", 
                    f"{model['likes']:,}", 
                    model.get('author', 'Unknown')
                )
            cli.console.print(table)
        return

    # Handle Ollama operations
    if args.ollama:
        cli.show_logo()
        ollama_args = args.ollama
        
        if len(ollama_args) == 1:
            if ollama_args[0] == "list":
                cli._list_ollama_models()
            elif ollama_args[0] == "quantizations":
                cli.ollama_manager.show_quantization_help()
            else:
                cli.console.print(f"[red]Invalid Ollama operation: {ollama_args[0]}[/red]")
        elif len(ollama_args) == 2:
            if ollama_args[0] == "search":
                cli._search_ollama_models(ollama_args[1])
            elif ollama_args[0] == "pull":
                cli._pull_ollama_model(ollama_args[1])
        return

    # Handle model loading (this will auto-start chat mode)
    if args.model:
        cli.show_logo()
        
        model_kwargs = {
            'model_type': "gguf" if args.gguf_file else "auto",
            'precision': args.type,
            'gguf_file': args.gguf_file,
            'context_length': args.context,
            'temperature': args.temperature,
            'top_p': args.top_p,
            'max_tokens': args.max_tokens
        }
        
        # Load model and auto-start premium chat
        model_loaded = cli.load_model(args.model, **model_kwargs)
        
        if not model_loaded:
            cli.console.print(f"[red]Failed to load model {args.model}. Exiting.[/red]")
            return
        
        # Handle special modes after loading
        if args.benchmark:
            cli.console.print(f"\n[{COGNICLI_ACCENT}]Running benchmark before starting chat...[/{COGNICLI_ACCENT}]")
            cli.benchmark_model()
            cli.console.print(f"\n[bold {COGNICLI_ACCENT}]Benchmark complete! Entering Premium Chat Mode...[/bold {COGNICLI_ACCENT}]")
            time.sleep(1)
        
        if args.generate:
            # Generate single response and stay in chat mode
            cli.console.print(f"\n[{COGNICLI_ACCENT}]Generating response for: {args.generate}[/{COGNICLI_ACCENT}]")
            cli.response_generator.generate_response(args.generate, stream=True, show_thinking=not args.no_think)
            cli.console.print(f"\n[bold {COGNICLI_ACCENT}]Response complete! Entering Premium Chat Mode...[/bold {COGNICLI_ACCENT}]")
            time.sleep(1)
        
        # Note: Premium chat mode is already started by load_model()
        return

    # Default behavior - show logo and welcome
    cli.show_logo()
    
    welcome_content = f"""
[bold {COGNICLI_ACCENT}]Welcome to CogniCLI v2.2.4 Premium![/bold {COGNICLI_ACCENT}] 🚀

[green]✨ Key Features:[/green]
• [bold]Auto-Chat Mode:[/bold] Load any model and instantly start premium chatting
• [bold]Beautiful Reasoning:[/bold] See AI thinking process with <think> blocks
• [bold]Advanced Tools:[/bold] File operations, code execution, and more
• [bold]Smart Detection:[/bold] Automatic Synapse model support
• [bold]Premium Interface:[/bold] Rich formatting and live response stats

[green]🚀 Quick Start:[/green]
• [bold]--model <id>[/bold]     Load a model and start premium chat instantly
• [bold]--search <query>[/bold] Search for models on Hugging Face
• [bold]--info <model>[/bold]   Show detailed model information
• [bold]--ollama list[/bold]    List available Ollama models

[bold {COGNICLI_ACCENT}]Examples:[/bold {COGNICLI_ACCENT}]
[dim]• cognicli --model gpt2                    # Load GPT-2 → Auto-start premium chat[/dim]
[dim]• cognicli --model microsoft/DialoGPT-medium --type q4  # Load with 4-bit quantization[/dim]
[dim]• cognicli --search llama2                 # Search for Llama models[/dim]
[dim]• cognicli --ollama pull llama2:q4_K_M     # Pull quantized model from Ollama[/dim]

[dim]🎯 Load any model to automatically enter Premium Chat Mode with beautiful reasoning display![/dim]
"""
    
    panel = Panel(
        welcome_content,
        title="🤖 Premium AI Command Line Interface",
        border_style=COGNICLI_ACCENT,
        padding=(1, 2),
    )
    
    cli.console.print(panel)

# Helper functions for Ollama operations in CLI class
def _list_ollama_models(self):
    """List all available Ollama models"""
    self.console.print(f"[{COGNICLI_ACCENT}]Listing Ollama models...[/{COGNICLI_ACCENT}]")
    models = self.ollama_manager.list_models()
    
    if not models:
        return
    
    table = Table(
        title="🦙 Available Ollama Models", 
        box=box.ROUNDED, 
        title_style=COGNICLI_ACCENT
    )
    table.add_column("Model Name", style=COGNICLI_ACCENT)
    table.add_column("Size", style="green")
    table.add_column("Modified", style="yellow")
    
    for model in models:
        size = self._format_size(model.get("size", 0))
        modified = model.get("modified_at", "Unknown")
        if modified != "Unknown":
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                modified = dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
        
        table.add_row(model["name"], size, modified)
    
    self.console.print(table)

def _search_ollama_models(self, query: str):
    """Search for Ollama models"""
    self.console.print(f"[{COGNICLI_ACCENT}]Searching Ollama for '{query}'...[/{COGNICLI_ACCENT}]")
    models = self.ollama_manager.search_models(query)
    
    if not models:
        self.console.print(f"[yellow]No Ollama models found matching '{query}'[/yellow]")
        return
    
    table = Table(
        title=f"🔍 Ollama Search Results for '{query}'", 
        box=box.ROUNDED, 
        title_style=COGNICLI_ACCENT
    )
    table.add_column("Model Name", style=COGNICLI_ACCENT)
    table.add_column("Description", style="green")
    table.add_column("Downloads", style="yellow", justify="right")
    
    for model in models:
        desc = model.get("description", "No description")
        if len(desc) > 50:
            desc = desc[:50] + "..."
        
        table.add_row(
            model["name"],
            desc,
            f"{model.get('downloads', 0):,}"
        )
    
    self.console.print(table)

def _pull_ollama_model(self, model_name: str, quantization: str = None):
    """Pull an Ollama model"""
    if quantization:
        full_name = f"{model_name}:{quantization}"
    else:
        full_name = model_name
    
    success = self.ollama_manager.pull_model(model_name, quantization)
    if success:
        self.console.print(f"[bold green]✅ Successfully pulled {full_name}[/bold green]")
    else:
        self.console.print(f"[red]❌ Failed to pull {full_name}[/red]")

# Add the helper methods to the CogniCLI class
CogniCLI._list_ollama_models = _list_ollama_models
CogniCLI._search_ollama_models = _search_ollama_models
CogniCLI._pull_ollama_model = _pull_ollama_model

if __name__ == "__main__":
    main()