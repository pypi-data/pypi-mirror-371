import re
from typing import Union, List


def latex_features(feature_names: Union[None, List[str]]) -> List[str]:
    if feature_names is None:
        return []

    greek_map = {
        'α': '\\alpha', 'β': '\\beta', 'γ': '\\gamma', 'δ': '\\delta',
        'ε': '\\epsilon', 'θ': '\\theta', 'λ': '\\lambda', 'μ': '\\mu',
        'ν': '\\nu', 'π': '\\pi', 'ρ': '\\rho', 'σ': '\\sigma', 'τ': '\\tau',
        'φ': '\\phi', 'χ': '\\chi', 'ψ': '\\psi', 'ω': '\\omega',
        'Δ': '\\Delta', 'Σ': '\\Sigma', 'Ω': '\\Omega', 'Γ': '\\Gamma',
        'Φ': '\\Phi', 'Ψ': '\\Psi', 'Ξ': '\\Xi',
        # ASCII stand-ins for Greek capitals without LaTeX commands
        'Β': 'B', 'Α': 'A', 'Ε': 'E', 'Ζ': 'Z', 'Η': 'H', 'Ι': 'I', 'Κ': 'K',
        'Μ': 'M', 'Ν': 'N', 'Ο': 'O', 'Ρ': 'P', 'Τ': 'T', 'Χ': 'X',
    }

    out = []
    for s in feature_names:
        s = str(s).rstrip()  # trim trailing spaces

        # Handle literal backslash sequences BEFORE other replacements
        # Replace literal \n, \t, \r etc. with underscores
        s = s.replace('\\n', '_').replace('\\t', '_').replace('\\r', '_')

        # Now handle actual newline/tab characters
        s = s.replace('\n', '_').replace('\t', '_').replace(' ', '_')

        # Remove any remaining backslashes that aren't part of our Greek mappings
        # This prevents them from being treated as LaTeX commands
        s = s.replace('\\', '_')

        # Drop bad filename chars
        s = re.sub(r'[<>:"/|?*]', '', s)

        # map Unicode Greek → LaTeX macros; keep ASCII; fallback to '?'
        buf = []
        for ch in s:
            if ch in greek_map:
                buf.append(greek_map[ch])
            elif ch.isascii():
                buf.append(ch)
            else:
                buf.append('?')
        s = ''.join(buf)

        # Only apply control word delimiting to valid LaTeX commands
        # This regex now only matches backslash followed by valid LaTeX command names
        # (starting with alpha, beta, gamma, etc.)
        valid_commands = '|'.join(['alpha', 'beta', 'gamma', 'delta', 'epsilon',
                                   'theta', 'lambda', 'mu', 'nu', 'pi', 'rho',
                                   'sigma', 'tau', 'phi', 'chi', 'psi', 'omega',
                                   'Delta', 'Sigma', 'Omega', 'Gamma', 'Phi',
                                   'Psi', 'Xi'])
        s = re.sub(rf'(\\(?:{valid_commands}))(?=[A-Za-z])', r'\1{}', s)

        # simple subscript heuristic: first '_' becomes _{...}; rest '_' -> '-'
        if '_' in s:
            base, rest = s.split('_', 1)
            s = f'{base}_{{{rest.replace("_", "-")}}}'

        # force math mode so \mu, subscripts, etc. are valid for usetex
        out.append(f'${s}$')
    return out


if __name__ == "__main__":
    # Example usage
    test_names = ["Phosphine_31P_NMR_shift", "PC_bend_max", "Phosphine_31P_NMR_shift_*_PC_bend_max", 'X_ε']
    latex_names = latex_features(test_names)
    print(latex_names)  # Should print LaTeX formatted feature names