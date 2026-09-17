#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import json

def auditar_github_real():
    print("=========================================================================")
    print("🐙 AUDITORÍA DE PUBLICACIONES REALES EN GITHUB (AUTOR: @me)")
    print("=========================================================================\n")

    query = """
    query {
      viewer {
        issueComments(first: 5, orderBy: {field: UPDATED_AT, direction: DESC}) {
          nodes {
            url
            body
            createdAt
            issue {
              number
              title
              body
              repository {
                nameWithOwner
              }
            }
          }
        }
      }
    }
    """

    try:
        cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)

        if res.returncode != 0:
            print(f"❌ Error al consultar la API de GitHub: {res.stderr.strip()}")
            return

        data = json.loads(res.stdout)
        comments = data.get("data", {}).get("viewer", {}).get("issueComments", {}).get("nodes", [])

        if not comments:
            print("ℹ️ La cuenta actual de GitHub no tiene comentarios recientes publicados en issues.")
            return

        for idx, c in enumerate(comments, 1):
            issue = c.get("issue", {})
            repo = issue.get("repository", {}).get("nameWithOwner", "Desconocido")
            title = issue.get("title", "Sin título")
            issue_body = issue.get("body", "Sin descripción disponible.")
            comment_body = c.get("body", "")
            url = c.get("url", "")
            created = c.get("createdAt", "")

            print(f"📌 [{idx}] REPOSITORIO: {repo} | Issue #{issue.get('number')}")
            print(f"   URL Comentario: {url}")
            print(f"   Fecha Envíado:  {created}")
            print(f"   Título Issue:   {title}")
            print("\n   📥 PETICIÓN ORIGINAL EN GITHUB:")
            for line in issue_body.split('\n')[:4]:
                print(f"      {line}")
            if len(issue_body.split('\n')) > 4:
                print("      [... cuerpo truncado ...]")

            print("\n   📤 RESPUESTA PUBLICADA POR CCIA2 EN GITHUB:")
            for line in comment_body.split('\n')[:8]:
                print(f"      {line}")
            if len(comment_body.split('\n')) > 8:
                print("      [... respuesta publicada truncada ...]")
            print("\n" + "=" * 73)

    except Exception as e:
        print(f"⚠️ Excepción durante la verificación: {e}")

if __name__ == '__main__':
    auditar_github_real()
