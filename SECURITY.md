# Política de Seguridad

- Reporta vulnerabilidades a `security@feria.local` usando cifrado PGP (clave en `docs/security-public-key.asc`).
- No abras issues públicos con detalles sensibles.
- Se confirma recepción en ≤48 h y se comparte plan de mitigación en ≤5 días laborales.
- Los parches críticos se publican bajo ventana coordinada; los créditos se otorgan tras la corrección.

## Buenas prácticas internas

- Aplica `pre-commit` antes de subir código.
- Usa secretos vía `configs/policies/` y gestores KMS/HSM.
- Ejecuta sandbox sin red y con listas blancas actualizadas.
- Mantén `docs/runbooks/` al día tras cada incidente de seguridad.
