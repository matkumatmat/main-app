# Plan: Refactor Algorithm Selection with Strategy Pattern & Dependency Injection

## Summary
Refactor packing_service.py to eliminate if-else algorithm selection by implementing Strategy Pattern with factory-based dependency injection, following the established app/pkg pattern conventions and hexagonal architecture principles.

## Context

### Current Problem (packing_service.py:313-318)
```python
if algorithm == "pure_dblf":
    return packer.pack_with_pure_dblf(legacy_items, bin_dims_int, max_trials, skip_scoring=True)
# elif algorithm == "incremental_beam_search":
#     return packer.pack_with_incremental_beam_search(legacy_items, bin_dims_int, max_trials)
# else:
#     return packer.pack_single_bin_with_trials(legacy_items, bin_dims_int, max_trials)
```

**Issues:**
- Violates Open/Closed Principle (must modify code to add algorithms)
- Tight coupling between service and algorithm implementations
- No dependency injection
- Nested if-else anti-pattern

### Existing app/pkg Pattern Analysis
**Discovered Patterns:**
- `pkg_exceptions.py`: Exception hierarchy with factory methods (`exception_wrapper`, `platform_error_confirmation`)
- `pkg_logger.py`: Factory class (`SecureLoggerFactory`) returning configured instances
- **Naming convention**: `pkg_<module_name>.py`
- **Structure**: Base classes + specialized implementations
- **Focus**: Hexagonal architecture (Ports & Adapters)

### Requirements
1. Use factory pattern from app/pkg convention
2. Enable algorithm injection (no if-else)
3. Focus on `pure_dblf` algorithm
4. Support future algorithms (beam_search, single_bin) without code modification
5. Follow hexagonal architecture principles

---

## Proposed Solution

### Phase 1: Create Packing Algorithm Abstraction Layer

#### 1.1 Create `app/pkg/algorithms/pkg_packing_algorithms.py`

**Port (Interface):**
```python
from abc import ABC, abstractmethod
from typing import Protocol
from dataclasses import dataclass

@dataclass
class PackingContext:
    """Context data passed to packing algorithms."""
    items: list
    bin_dimensions: tuple[int, int, int]
    max_trials: int
    skip_scoring: bool = False

@dataclass
class PackingResult:
    """Result returned from packing algorithms."""
    bins_data: list[dict]
    metadata: dict

class IPackingAlgorithm(ABC):
    """
    Port (Interface) for packing algorithms.

    All packing algorithms must implement this interface to be
    registered in the factory and used by the packing service.
    """

    @property
    @abstractmethod
    def algorithm_name(self) -> str:
        """Unique identifier for this algorithm."""
        pass

    @abstractmethod
    def pack(
        self,
        packer: 'MultiBinPacker',  # Dependency injection
        context: PackingContext
    ) -> PackingResult:
        """
        Execute packing algorithm.

        Args:
            packer: MultiBinPacker instance (injected dependency)
            context: Packing parameters

        Returns:
            PackingResult with bins data and metadata
        """
        pass
```

**Adapter (Implementations):**
```python
class PureDBLFAlgorithm(IPackingAlgorithm):
    """
    Adapter for Pure DBLF (Deepest Bottom Left Fill) algorithm.

    Wraps the existing MultiBinPacker.pack_with_pure_dblf method.
    """

    @property
    def algorithm_name(self) -> str:
        return "pure_dblf"

    def pack(
        self,
        packer: 'MultiBinPacker',
        context: PackingContext
    ) -> PackingResult:
        """Execute Pure DBLF packing."""
        bins_data = packer.pack_with_pure_dblf(
            context.items,
            context.bin_dimensions,
            context.max_trials,
            skip_scoring=context.skip_scoring
        )

        return PackingResult(
            bins_data=bins_data,
            metadata={
                "algorithm": self.algorithm_name,
                "items_count": len(context.items),
                "max_trials": context.max_trials
            }
        )

class IncrementalBeamSearchAlgorithm(IPackingAlgorithm):
    """Adapter for Incremental Beam Search algorithm (future)."""

    @property
    def algorithm_name(self) -> str:
        return "incremental_beam_search"

    def pack(
        self,
        packer: 'MultiBinPacker',
        context: PackingContext
    ) -> PackingResult:
        bins_data = packer.pack_with_incremental_beam_search(
            context.items,
            context.bin_dimensions,
            context.max_trials
        )
        return PackingResult(bins_data=bins_data, metadata={"algorithm": self.algorithm_name})

class SingleBinTrialsAlgorithm(IPackingAlgorithm):
    """Adapter for single bin trials algorithm (future)."""

    @property
    def algorithm_name(self) -> str:
        return "single_bin_trials"

    def pack(
        self,
        packer: 'MultiBinPacker',
        context: PackingContext
    ) -> PackingResult:
        bins_data = packer.pack_single_bin_with_trials(
            context.items,
            context.bin_dimensions,
            context.max_trials
        )
        return PackingResult(bins_data=bins_data, metadata={"algorithm": self.algorithm_name})
```

**Factory:**
```python
from app.pkg.exceptions.pkg_exceptions import ValidationError

class PackingAlgorithmFactory:
    """
    Factory for creating and managing packing algorithm instances.

    Follows the pkg pattern established in app/pkg/logs/pkg_logger.py
    (SecureLoggerFactory).

    Usage:
        factory = PackingAlgorithmFactory()
        factory.register(PureDBLFAlgorithm())
        algorithm = factory.get("pure_dblf")
        result = algorithm.pack(packer, context)
    """

    def __init__(self):
        self._algorithms: dict[str, IPackingAlgorithm] = {}
        self._default_algorithm: str | None = None

    def register(self, algorithm: IPackingAlgorithm, set_as_default: bool = False) -> None:
        """
        Register a packing algorithm.

        Args:
            algorithm: Algorithm instance implementing IPackingAlgorithm
            set_as_default: If True, sets this as the default algorithm

        Raises:
            ValidationError: If algorithm name already registered
        """
        if algorithm.algorithm_name in self._algorithms:
            raise ValidationError(
                message=f"Algorithm '{algorithm.algorithm_name}' already registered",
                field="algorithm_name",
                value=algorithm.algorithm_name
            )

        self._algorithms[algorithm.algorithm_name] = algorithm

        if set_as_default or self._default_algorithm is None:
            self._default_algorithm = algorithm.algorithm_name

    def get(self, algorithm_name: str | None = None) -> IPackingAlgorithm:
        """
        Get algorithm by name.

        Args:
            algorithm_name: Name of algorithm (uses default if None)

        Returns:
            Algorithm instance

        Raises:
            ValidationError: If algorithm not found
        """
        name = algorithm_name or self._default_algorithm

        if not name:
            raise ValidationError(
                message="No algorithm specified and no default algorithm set",
                field="algorithm_name"
            )

        if name not in self._algorithms:
            available = list(self._algorithms.keys())
            raise ValidationError(
                message=f"Algorithm '{name}' not found",
                field="algorithm_name",
                value=name,
                constraint=f"Available algorithms: {', '.join(available)}"
            )

        return self._algorithms[name]

    def list_algorithms(self) -> list[str]:
        """List all registered algorithm names."""
        return list(self._algorithms.keys())

    @property
    def default_algorithm(self) -> str | None:
        """Get default algorithm name."""
        return self._default_algorithm

# Global factory instance (singleton pattern)
_algorithm_factory: PackingAlgorithmFactory | None = None

def get_algorithm_factory() -> PackingAlgorithmFactory:
    """
    Get or create the global algorithm factory instance.

    Returns:
        Configured PackingAlgorithmFactory

    Usage:
        factory = get_algorithm_factory()
        algorithm = factory.get("pure_dblf")
    """
    global _algorithm_factory

    if _algorithm_factory is None:
        _algorithm_factory = PackingAlgorithmFactory()

        # Register default algorithms
        _algorithm_factory.register(PureDBLFAlgorithm(), set_as_default=True)
        # Future algorithms can be registered here when implemented:
        # _algorithm_factory.register(IncrementalBeamSearchAlgorithm())
        # _algorithm_factory.register(SingleBinTrialsAlgorithm())

    return _algorithm_factory
```

#### 1.2 Create `app/pkg/algorithms/__init__.py`

```python
"""
Packing algorithms abstraction layer.

Provides factory-based dependency injection for packing algorithms
following the hexagonal architecture pattern.
"""

from app.pkg.algorithms.pkg_packing_algorithms import (
    # Ports (Interfaces)
    IPackingAlgorithm,
    PackingContext,
    PackingResult,

    # Adapters (Implementations)
    PureDBLFAlgorithm,
    IncrementalBeamSearchAlgorithm,
    SingleBinTrialsAlgorithm,

    # Factory
    PackingAlgorithmFactory,
    get_algorithm_factory,
)

__all__ = [
    # Ports
    "IPackingAlgorithm",
    "PackingContext",
    "PackingResult",

    # Adapters
    "PureDBLFAlgorithm",
    "IncrementalBeamSearchAlgorithm",
    "SingleBinTrialsAlgorithm",

    # Factory
    "PackingAlgorithmFactory",
    "get_algorithm_factory",
]
```

### Phase 2: Refactor PackingService

#### 2.1 Update `src/domain/services/packing_service.py`

**Replace lines 285-319 with:**

```python
from app.pkg.algorithms import get_algorithm_factory, PackingContext

def _execute_packing_legacy_fast(self, items, bin_dimensions, algorithm, max_trials):
    """
    Fast packing - skip scoring calculation.

    Uses dependency injection via algorithm factory.
    No if-else branching for algorithm selection.
    """
    # Convert API items to legacy format
    legacy_items = []
    for item in items:
        color = item.properties.color.lstrip('#')
        class_map = {"food": 1, "chemical": 2, "neutral": 3, "frozen": 4, "electronics": 5}

        legacy_item = Item(
            id=item.properties.item_id,
            l=int(round(item.width)),
            w=int(round(item.depth)),
            h=int(round(item.height)),
            color=color,
            weight=float(item.properties.weight_kg * 1000) if item.properties.weight_kg else 100.0,
            is_fragile=item.properties.is_fragile,
            class_id=class_map.get(item.properties.class_id, 3),
            delivery_seq=5, max_load=10000.0, stacking_surface_ratio=0.5, group_id=0,
            can_spin=item.properties.can_spin,
            can_sleep=item.properties.can_sleep
        )
        legacy_items.append(legacy_item)

    # Prepare packer and context
    bin_dims_int = (
        int(round(bin_dimensions[0])),
        int(round(bin_dimensions[1])),
        int(round(bin_dimensions[2]))
    )
    packer = MultiBinPacker(beam_width=5)

    # Store packer instance for background scoring
    self._last_multi_bin_packer = packer

    # Get algorithm via factory (DEPENDENCY INJECTION - NO IF-ELSE)
    factory = get_algorithm_factory()
    algorithm_instance = factory.get(algorithm)  # Raises ValidationError if not found

    # Create packing context
    context = PackingContext(
        items=legacy_items,
        bin_dimensions=bin_dims_int,
        max_trials=max_trials,
        skip_scoring=True
    )

    # Execute algorithm (Strategy Pattern)
    result = algorithm_instance.pack(packer, context)

    return result.bins_data
```

**Benefits:**
- ✅ No if-else branching
- ✅ Dependency injection via factory
- ✅ Open/Closed Principle: add algorithms without modifying this code
- ✅ Strategy Pattern: algorithms are interchangeable
- ✅ Validation error if unknown algorithm requested

### Phase 3: Project Structure

```
app/
├── pkg/                           # Shared packages (follows established pattern)
│   ├── algorithms/                # ⭐ NEW: Packing algorithms abstraction
│   │   ├── __init__.py
│   │   └── pkg_packing_algorithms.py
│   ├── exceptions/
│   │   ├── __init___.py
│   │   └── pkg_exceptions.py
│   ├── logs/
│   │   ├── __init__.py
│   │   └── pkg_logger.py
│   ├── secure/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── concurrency.py
│   │   ├── datetime.py
│   │   ├── string_enum.py
│   │   └── uuid.py
│   └── __init__.py

src/
├── domain/
│   └── services/
│       ├── packing_service.py     # ⭐ REFACTORED: Uses algorithm factory
│       ├── converter_service.py
│       └── data_persistence_service.py

solver/                            # Legacy algorithms (adapters wrap these)
├── packer.py
├── pure_dblf.py
└── ...
```

---

## Critical Files to Modify

1. **CREATE:** `app/pkg/algorithms/pkg_packing_algorithms.py` (~200 lines)
2. **CREATE:** `app/pkg/algorithms/__init__.py` (~30 lines)
3. **MODIFY:** `src/domain/services/packing_service.py` (lines 285-319)

---

## Implementation Order

### Step 1: Create Algorithm Abstraction (app/pkg/algorithms/)
1. Create directory: `app/pkg/algorithms/`
2. Implement `pkg_packing_algorithms.py` with:
   - `IPackingAlgorithm` interface (Port)
   - `PackingContext` & `PackingResult` data classes
   - `PureDBLFAlgorithm` adapter (wraps existing solver)
   - `PackingAlgorithmFactory` with registration
   - `get_algorithm_factory()` singleton getter
3. Create `__init__.py` for clean exports

### Step 2: Refactor PackingService
1. Import `get_algorithm_factory`, `PackingContext`
2. Replace `_execute_packing_legacy_fast()` lines 285-319
3. Remove if-else block
4. Use factory.get(algorithm) for dependency injection

### Step 3: Add Future Algorithms (Commented/Stubbed)
1. Add `IncrementalBeamSearchAlgorithm` (commented in factory registration)
2. Add `SingleBinTrialsAlgorithm` (commented in factory registration)
3. Document how to enable them when solver methods are ready

---

## Testing Strategy

### Unit Tests
```python
def test_algorithm_factory_registration():
    """Test algorithm registration and retrieval."""
    factory = PackingAlgorithmFactory()
    algorithm = PureDBLFAlgorithm()
    factory.register(algorithm, set_as_default=True)

    retrieved = factory.get("pure_dblf")
    assert retrieved is algorithm
    assert factory.default_algorithm == "pure_dblf"

def test_algorithm_factory_validation():
    """Test validation error for unknown algorithm."""
    factory = get_algorithm_factory()

    with pytest.raises(ValidationError) as exc:
        factory.get("nonexistent_algorithm")

    assert "not found" in str(exc.value)

def test_pure_dblf_algorithm_execution():
    """Test Pure DBLF algorithm executes correctly."""
    from solver.packer import MultiBinPacker

    packer = MultiBinPacker(beam_width=5)
    algorithm = PureDBLFAlgorithm()
    context = PackingContext(
        items=[...],  # test items
        bin_dimensions=(490, 350, 440),
        max_trials=10,
        skip_scoring=True
    )

    result = algorithm.pack(packer, context)

    assert isinstance(result, PackingResult)
    assert result.metadata["algorithm"] == "pure_dblf"
    assert len(result.bins_data) > 0
```

### Integration Test
```python
def test_packing_service_uses_factory():
    """Test PackingService uses algorithm factory (no if-else)."""
    service = PackingService()

    # Should work for "pure_dblf"
    response = service.pack(request_with_algorithm="pure_dblf")
    assert response.success

    # Should raise ValidationError for unknown algorithm
    with pytest.raises(ValidationError):
        service.pack(request_with_algorithm="invalid_algo")
```

### Manual Verification
1. Start API: `python api.py`
2. Send request with `algorithm: "pure_dblf"` → Should work
3. Send request with `algorithm: "unknown"` → Should return ValidationError
4. Check logs: No if-else execution paths logged

---

## Benefits Summary

### Before (Current State)
```python
if algorithm == "pure_dblf":
    return packer.pack_with_pure_dblf(...)
# elif algorithm == "incremental_beam_search":
#     return packer.pack_with_incremental_beam_search(...)
```
- ❌ Violates Open/Closed Principle
- ❌ Tight coupling
- ❌ Must modify code to add algorithms
- ❌ No dependency injection

### After (Proposed Solution)
```python
factory = get_algorithm_factory()
algorithm_instance = factory.get(algorithm)
result = algorithm_instance.pack(packer, context)
return result.bins_data
```
- ✅ Follows Open/Closed Principle
- ✅ Dependency injection via factory
- ✅ Strategy Pattern for interchangeable algorithms
- ✅ Add algorithms by registering, not modifying code
- ✅ Follows hexagonal architecture (Ports & Adapters)
- ✅ Consistent with app/pkg pattern conventions
- ✅ Clean, testable, maintainable

---

## Risks & Mitigation

### Risk 1: Breaking Existing API
**Mitigation:** Behavior remains identical. Factory.get("pure_dblf") calls same underlying method.

### Risk 2: Performance Overhead from Factory
**Mitigation:** Factory is singleton, algorithm lookup is O(1) dict access. Negligible overhead.

### Risk 3: Incomplete Algorithm Implementations
**Mitigation:** Only register `PureDBLFAlgorithm` by default. Others commented until solver methods ready.

---

## Next Steps

1. **User Approval:** Review this plan
2. **Implementation:** Create algorithm abstraction layer
3. **Refactoring:** Update packing_service.py
4. **Testing:** Unit + integration tests
5. **Documentation:** Update API docs with algorithm names
