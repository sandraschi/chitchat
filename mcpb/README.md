# chitchat (MCPB Bundle)

Chitchat — conversation starters, archive, and fleet docs crosslink

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "chitchat": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "chitchat"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **api_health**: api_health
- **api_welcome**: api_welcome
- **api_topics**: api_topics
- **api_archive_list**: api_archive_list
- **api_archive_get**: api_archive_get
- **api_archive_add**: api_archive_add
- **api_archive_delete**: api_archive_delete
- **api_archive_stats**: api_archive_stats
- **api_docs_search**: api_docs_search
- **api_docs_health**: api_docs_health
- **chitchat_welcome**: chitchat_welcome
- **chitchat_topics**: chitchat_topics
- **chitchat_archive**: chitchat_archive
- **chitchat_search_docs**: chitchat_search_docs

## Requirements

- Python 3.12+
- uv
