import json
import os
import subprocess
import re
from typing import Any, Dict, List, Optional

import toml


import logging


class CrateAnalyzer:
    def __init__(self, crate_source_path: str):
        self.crate_source_path = crate_source_path
        self.logger = logging.getLogger(__name__)

    def run_cargo_cmd(self, cmd, timeout=600) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                cmd,
                cwd=self.crate_source_path,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "cmd": " ".join(cmd),
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {"cmd": " ".join(cmd), "error": str(e)}

    def run_cargo_cmd_with_fallback(
        self,
        primary_cmd: List[str],
        fallback_cmd: Optional[List[str]] = None,
        timeout=600,
    ) -> Dict[str, Any]:
        """Run cargo command with fallback if primary fails."""
        result = self.run_cargo_cmd(primary_cmd, timeout)

        # If primary command failed and we have a fallback, try it
        if result.get("returncode", 0) != 0 and fallback_cmd:
            self.logger.info(
                f"Primary command failed, trying fallback: {' '.join(fallback_cmd)}"
            )
            fallback_result = self.run_cargo_cmd(fallback_cmd, timeout)
            fallback_result["used_fallback"] = True
            return fallback_result

        return result

    def _calculate_quality_score(
        self, warnings: List[Dict], errors: List[Dict], suggestions: List[Dict]
    ) -> float:
        """Calculate a quality score based on analysis results."""
        base_score = 1.0

        # Deduct points for errors (most severe)
        error_penalty = len(errors) * 0.1
        base_score -= min(error_penalty, 0.5)  # Cap at 50% penalty for errors

        # Deduct points for warnings (moderate)
        warning_penalty = len(warnings) * 0.02
        base_score -= min(warning_penalty, 0.3)  # Cap at 30% penalty for warnings

        # Small bonus for suggestions (shows good practices)
        suggestion_bonus = min(len(suggestions) * 0.005, 0.1)  # Cap at 10% bonus
        base_score += suggestion_bonus

        return max(0.0, min(1.0, base_score))  # Ensure score is between 0 and 1

    def _is_critical_issue(self, message: Dict) -> bool:
        """Determine if a clippy/compiler message represents a critical issue."""
        critical_patterns = [
            r"unsafe",
            r"unchecked",
            r"panic",
            r"unreachable",
            r"dead_code",
            r"unused_imports",
            r"missing_docs",
            r"clippy::all",
            r"clippy::pedantic",
        ]

        message_text = message.get("message", {}).get("message", "").lower()
        for pattern in critical_patterns:
            if re.search(pattern, message_text):
                return True
        return False

    def process_clippy_results(self, clippy_output: List[Dict]) -> Dict[str, Any]:
        """Process clippy results into actionable insights."""
        warnings = []
        errors = []
        suggestions = []
        critical_issues = []

        for message in clippy_output:
            msg_data = message.get("message", {})
            level = msg_data.get("level", "unknown")

            if level == "warning":
                warnings.append(message)
                if self._is_critical_issue(message):
                    critical_issues.append(message)
            elif level == "error":
                errors.append(message)
                critical_issues.append(message)
            elif level == "help":
                suggestions.append(message)

        quality_score = self._calculate_quality_score(warnings, errors, suggestions)

        return {
            "warning_count": len(warnings),
            "error_count": len(errors),
            "suggestion_count": len(suggestions),
            "critical_issue_count": len(critical_issues),
            "quality_score": quality_score,
            "critical_issues": critical_issues[:10],  # Limit to first 10 for storage
            "warnings": warnings[:20],  # Limit to first 20
            "errors": errors[:10],  # Limit to first 10
            "suggestions": suggestions[:10],  # Limit to first 10
        }

    def process_audit_results(self, audit_output: str) -> Dict[str, Any]:
        """Process cargo audit results."""
        try:
            audit_data = json.loads(audit_output)
            vulnerabilities = audit_data.get("vulnerabilities", [])
            advisories = audit_data.get("advisories", {})

            return {
                "vulnerability_count": len(vulnerabilities),
                "advisory_count": len(advisories),
                "vulnerabilities": vulnerabilities,
                "advisories": list(advisories.values())[:10],  # Limit to first 10
                "risk_level": self._calculate_security_risk_level(vulnerabilities),
                "has_critical_vulnerabilities": any(
                    isinstance(v, dict) and v.get("cvss", {}).get("score", 0) >= 9.0
                    for v in vulnerabilities
                ),
            }
        except (json.JSONDecodeError, KeyError):
            return {
                "vulnerability_count": 0,
                "advisory_count": 0,
                "risk_level": "unknown",
                "error": "Failed to parse audit results",
            }

    def process_geiger_results(self, geiger_output: str) -> Dict[str, Any]:
        """Process cargo-geiger results for unsafe code analysis."""
        try:
            geiger_data = json.loads(geiger_output)
            packages = geiger_data.get("packages", [])

            total_unsafe_functions = 0
            total_unsafe_expressions = 0
            total_unsafe_impls = 0
            total_unsafe_methods = 0
            packages_with_unsafe = 0
            packages_forbidding_unsafe = 0

            for package in packages:
                unsafety = package.get("unsafety", {})
                used = unsafety.get("used", {})

                # Count unsafe usage
                unsafe_functions = used.get("functions", {}).get("unsafe_", 0)
                unsafe_expressions = used.get("exprs", {}).get("unsafe_", 0)
                unsafe_impls = used.get("item_impls", {}).get("unsafe_", 0)
                unsafe_methods = used.get("methods", {}).get("unsafe_", 0)

                total_unsafe_functions += unsafe_functions
                total_unsafe_expressions += unsafe_expressions
                total_unsafe_impls += unsafe_impls
                total_unsafe_methods += unsafe_methods

                if any(
                    [unsafe_functions, unsafe_expressions, unsafe_impls, unsafe_methods]
                ):
                    packages_with_unsafe += 1

                if unsafety.get("forbids_unsafe", False):
                    packages_forbidding_unsafe += 1

            total_unsafe_items = (
                total_unsafe_functions
                + total_unsafe_expressions
                + total_unsafe_impls
                + total_unsafe_methods
            )

            # Calculate safety score (0-1, higher is safer)
            if total_unsafe_items == 0:
                safety_score = 1.0
            else:
                # Penalize based on unsafe usage, but don't go below 0.3
                safety_score = max(0.3, 1.0 - (total_unsafe_items * 0.01))

            return {
                "total_unsafe_items": total_unsafe_items,
                "unsafe_functions": total_unsafe_functions,
                "unsafe_expressions": total_unsafe_expressions,
                "unsafe_impls": total_unsafe_impls,
                "unsafe_methods": total_unsafe_methods,
                "packages_with_unsafe": packages_with_unsafe,
                "packages_forbidding_unsafe": packages_forbidding_unsafe,
                "total_packages": len(packages),
                "safety_score": safety_score,
                "has_unsafe_code": total_unsafe_items > 0,
                "risk_level": (
                    "high"
                    if total_unsafe_items > 50
                    else "medium" if total_unsafe_items > 10 else "low"
                ),
            }
        except (json.JSONDecodeError, KeyError):
            return {
                "total_unsafe_items": 0,
                "safety_score": 1.0,
                "has_unsafe_code": False,
                "risk_level": "unknown",
                "error": "Failed to parse geiger results",
            }

    def _calculate_security_risk_level(self, vulnerabilities: List[Dict]) -> str:
        """Calculate security risk level based on vulnerabilities."""
        if not vulnerabilities:
            return "low"

        # Handle case where vulnerabilities might be strings or other types
        cvss_scores = []
        for v in vulnerabilities:
            if isinstance(v, dict):
                cvss_score = v.get("cvss", {}).get("score", 0)
                if isinstance(cvss_score, (int, float)):
                    cvss_scores.append(cvss_score)

        if not cvss_scores:
            return "low"

        max_cvss = max(cvss_scores)

        if max_cvss >= 9.0:
            return "critical"
        elif max_cvss >= 7.0:
            return "high"
        elif max_cvss >= 4.0:
            return "medium"
        else:
            return "low"

    def analyze(self) -> Dict[str, Any]:
        results = {}

        # Basic build and test analysis
        results["build"] = self.run_cargo_cmd_with_fallback(
            ["cargo", "+stable", "build", "--all-features"],
            ["cargo", "build", "--all-features"],
        )
        results["test"] = self.run_cargo_cmd_with_fallback(
            ["cargo", "+stable", "test", "--all-features"],
            ["cargo", "test", "--all-features"],
        )

        # Enhanced linting and formatting
        results["clippy"] = self.run_cargo_cmd_with_fallback(
            [
                "cargo",
                "+stable",
                "clippy",
                "--all-features",
                "--",
                "-D",
                "warnings",
                "-D",
                "clippy::all",
            ],
            ["cargo", "clippy", "--all-features", "--", "-D", "warnings"],
        )
        results["fmt"] = self.run_cargo_cmd_with_fallback(
            ["cargo", "+stable", "fmt", "--", "--check"],
            ["cargo", "fmt", "--", "--check"],
        )

        # Security analysis
        results["audit"] = self.run_cargo_cmd_with_fallback(
            ["cargo", "+stable", "audit", "--json"], ["cargo", "audit", "--json"]
        )

        # Additional security tools (if available)
        results["geiger"] = self.run_cargo_cmd_with_fallback(
            ["cargo", "geiger", "--output-format", "Json"],
            None,  # No fallback for geiger
        )

        # Dependency analysis
        results["tree"] = self.run_cargo_cmd_with_fallback(
            ["cargo", "+stable", "tree"], ["cargo", "tree"]
        )
        results["outdated"] = self.run_cargo_cmd_with_fallback(
            ["cargo", "outdated", "--format", "json"], None  # No fallback for outdated
        )

        # Documentation
        results["doc"] = self.run_cargo_cmd_with_fallback(
            ["cargo", "+stable", "doc", "--no-deps"], ["cargo", "doc", "--no-deps"]
        )

        # License analysis
        results["license"] = self.run_cargo_cmd_with_fallback(
            ["cargo", "license", "--json"], None  # No fallback for license
        )

        # Code coverage (if tarpaulin is available)
        results["coverage"] = self.run_cargo_cmd_with_fallback(
            ["cargo", "tarpaulin", "--out", "json"], None  # No fallback for tarpaulin
        )

        # Process results for insights
        results["insights"] = self._generate_insights(results)

        # Provenance
        vcs_info_path = os.path.join(self.crate_source_path, ".cargo_vcs_info.json")
        if os.path.exists(vcs_info_path):
            with open(vcs_info_path) as f:
                results["vcs_info"] = f.read()

        # Metadata
        cargo_toml = os.path.join(self.crate_source_path, "Cargo.toml")
        if os.path.exists(cargo_toml):
            with open(cargo_toml) as f:
                results["metadata"] = toml.load(f)

        return results

    def _generate_insights(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from analysis results."""
        insights = {
            "overall_quality_score": 0.0,
            "security_risk_level": "unknown",
            "maintenance_health": "unknown",
            "code_quality": "unknown",
            "recommendations": [],
        }

        # Process clippy results if available
        if results.get("clippy", {}).get("stdout"):
            try:
                clippy_data = json.loads(results["clippy"]["stdout"])
                clippy_insights = self.process_clippy_results(clippy_data)
                insights["clippy_insights"] = clippy_insights
                insights["overall_quality_score"] = clippy_insights["quality_score"]
            except (json.JSONDecodeError, KeyError):
                pass

        # Process audit results if available
        if results.get("audit", {}).get("stdout"):
            audit_insights = self.process_audit_results(results["audit"]["stdout"])
            insights["audit_insights"] = audit_insights
            insights["security_risk_level"] = audit_insights["risk_level"]

        # Process geiger results if available
        if results.get("geiger", {}).get("stdout"):
            geiger_insights = self.process_geiger_results(results["geiger"]["stdout"])
            insights["geiger_insights"] = geiger_insights

            # Adjust security risk level based on unsafe code
            if geiger_insights.get("has_unsafe_code", False):
                current_risk = insights.get("security_risk_level", "low")
                if current_risk == "low" and geiger_insights.get("risk_level") in [
                    "medium",
                    "high",
                ]:
                    insights["security_risk_level"] = geiger_insights["risk_level"]

        # Determine maintenance health
        build_success = results.get("build", {}).get("returncode", 1) == 0
        test_success = results.get("test", {}).get("returncode", 1) == 0
        fmt_success = results.get("fmt", {}).get("returncode", 1) == 0

        if build_success and test_success and fmt_success:
            insights["maintenance_health"] = "excellent"
        elif build_success and test_success:
            insights["maintenance_health"] = "good"
        elif build_success:
            insights["maintenance_health"] = "fair"
        else:
            insights["maintenance_health"] = "poor"

        # Determine code quality
        quality_score = insights["overall_quality_score"]
        if quality_score >= 0.8:
            insights["code_quality"] = "excellent"
        elif quality_score >= 0.6:
            insights["code_quality"] = "good"
        elif quality_score >= 0.4:
            insights["code_quality"] = "fair"
        else:
            insights["code_quality"] = "poor"

        # Generate recommendations
        recommendations = []

        if insights.get("clippy_insights", {}).get("critical_issue_count", 0) > 0:
            recommendations.append("Address critical clippy warnings")

        if insights.get("audit_insights", {}).get("vulnerability_count", 0) > 0:
            recommendations.append("Update dependencies with security vulnerabilities")

        if insights.get("geiger_insights", {}).get("has_unsafe_code", False):
            unsafe_count = insights.get("geiger_insights", {}).get(
                "total_unsafe_items", 0
            )
            recommendations.append(
                f"Review {unsafe_count} unsafe code items detected by cargo-geiger"
            )

        if not build_success:
            recommendations.append("Fix build errors")

        if not test_success:
            recommendations.append("Fix failing tests")

        if not fmt_success:
            recommendations.append("Run cargo fmt to fix formatting issues")

        insights["recommendations"] = recommendations

        return insights
