"""Recherche bibliographique PubMed pour SENTOX Science Check V2.

Utilise les E-utilities publiques de NCBI.
Les métadonnées récupérées ne constituent pas une validation automatique
de la qualité méthodologique ou des conclusions d'une publication.
"""

import json
import os
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
TOOL_NAME = "SENTOXScienceCheck"


class PubMedError(Exception):
    """Erreur de recherche ou de récupération PubMed."""


def _requete_ncbi(endpoint, parametres, timeout=20):
    """Envoie une requête GET aux E-utilities NCBI."""
    params = dict(parametres)
    params["tool"] = TOOL_NAME

    email = os.environ.get("SENTOX_CONTACT_EMAIL", "").strip()
    if email:
        params["email"] = email

    url = BASE_URL + endpoint + "?" + urllib.parse.urlencode(params)
    requete = urllib.request.Request(
        url,
        headers={"User-Agent": "SENTOXScienceCheck/2.0"}
    )

    try:
        with urllib.request.urlopen(requete, timeout=timeout) as reponse:
            return reponse.read()
    except (urllib.error.URLError, TimeoutError, OSError) as erreur:
        raise PubMedError(
            "Connexion PubMed impossible. Vérifiez l'accès Internet et réessayez."
        ) from erreur


def rechercher_pubmed(termes, limite=10):
    """Recherche des articles PubMed et retourne leurs métadonnées.

    Args:
        termes: mots-clés ou expression de recherche.
        limite: nombre maximal d'articles à récupérer (1 à 20).

    Returns:
        dict avec la requête, le nombre de résultats et les articles.
    """
    termes = (termes or "").strip()
    if not termes:
        raise ValueError("Saisissez des mots-clés pour la recherche PubMed.")

    try:
        limite = int(limite)
    except (TypeError, ValueError) as erreur:
        raise ValueError("La limite doit être un nombre entier.") from erreur

    limite = max(1, min(limite, 20))

    donnees = _requete_ncbi(
        "esearch.fcgi",
        {
            "db": "pubmed",
            "term": termes,
            "retmax": limite,
            "retmode": "json",
            "sort": "relevance",
        },
    )

    try:
        resultat_json = json.loads(donnees.decode("utf-8"))
        recherche = resultat_json["esearchresult"]
        identifiants = recherche.get("idlist", [])
        total = int(recherche.get("count", 0))
    except (ValueError, KeyError, TypeError) as erreur:
        raise PubMedError("Réponse de recherche PubMed non reconnue.") from erreur

    if not identifiants:
        return {
            "source": "PubMed / NCBI",
            "requete": termes,
            "nombre_total": total,
            "nombre_recupere": 0,
            "articles": [],
            "avertissement": (
                "Aucun article trouvé pour cette requête. "
                "Cela ne prouve pas qu'aucune étude n'existe."
            ),
        }

    xml = _requete_ncbi(
        "efetch.fcgi",
        {
            "db": "pubmed",
            "id": ",".join(identifiants),
            "retmode": "xml",
        },
    )

    try:
        racine = ET.fromstring(xml)
    except ET.ParseError as erreur:
        raise PubMedError("Les données bibliographiques reçues sont illisibles.") from erreur

    articles = []

    for article_xml in racine.findall(".//PubmedArticle"):
        titre = " ".join(
            "".join(article_xml.find("MedlineCitation/Article/ArticleTitle").itertext()).split()
        ) if article_xml.find("MedlineCitation/Article/ArticleTitle") is not None else "Titre indisponible"

        pmid_node = article_xml.find(".//PMID")
        pmid = pmid_node.text.strip() if pmid_node is not None and pmid_node.text else ""

        journal_node = article_xml.find(".//Journal/Title")
        journal = journal_node.text.strip() if journal_node is not None and journal_node.text else ""

        annee = ""
        for chemin in (
            ".//Journal/JournalIssue/PubDate/Year",
            ".//Journal/JournalIssue/PubDate/MedlineDate",
            ".//PubmedData/History/PubMedPubDate/Year",
        ):
            noeud = article_xml.find(chemin)
            if noeud is not None and noeud.text:
                annee = noeud.text.strip()[:4]
                break

        auteurs = []
        for auteur in article_xml.findall(".//Article/AuthorList/Author"):
            collectif = auteur.findtext("CollectiveName")
            prenom = auteur.findtext("ForeName", "")
            nom = auteur.findtext("LastName", "")
            nom_complet = " ".join(part for part in (prenom, nom) if part).strip()
            nom_complet = collectif or nom_complet
            if nom_complet:
                auteurs.append(nom_complet)

        resume = []
        for element in article_xml.findall(".//Article/Abstract/AbstractText"):
            texte = " ".join("".join(element.itertext()).split())
            if texte:
                section = element.attrib.get("Label", "").strip()
                resume.append(
                    f"{section}: {texte}" if section else texte
                )

        doi = ""
        for identifiant in article_xml.findall(".//PubmedData/ArticleIdList/ArticleId"):
            if identifiant.attrib.get("IdType") == "doi" and identifiant.text:
                doi = identifiant.text.strip()
                break

        articles.append({
            "pmid": pmid,
            "titre": titre,
            "auteurs": auteurs,
            "annee": annee,
            "revue": journal,
            "doi": doi,
            "resume": " ".join(resume),
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
            "source": "PubMed / NCBI",
            "qualite_evaluee": False,
        })

    return {
        "source": "PubMed / NCBI",
        "requete": termes,
        "nombre_total": total,
        "nombre_recupere": len(articles),
        "articles": articles,
        "avertissement": (
            "Résultats bibliographiques automatiques : la pertinence de chaque "
            "article, sa qualité méthodologique et ses conclusions doivent être "
            "évaluées séparément. L'absence de résumé ne signifie pas absence d'étude."
        ),
    }
