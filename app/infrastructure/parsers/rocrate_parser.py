class ROCrateParser:
    SUPPORTED_EXTENSIONS = (".pdf", ".docx", ".rtf")

    def extract_supported_files(self, ro_crate_json: dict) -> list[str]:
        graph = ro_crate_json.get("@graph", [])
        
        return [
            item["@id"]
            for item in graph
            if item.get("@type") == "File"
            and item.get("@id", "").lower().endswith(self.SUPPORTED_EXTENSIONS)
        ]

