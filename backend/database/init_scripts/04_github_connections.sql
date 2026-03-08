-- Add new columns to projects table for GitHub connection methods
DO
  $ $
  BEGIN
    -- Add github_connection_type if not exists
    IF NOT EXISTS (
      SELECT
        1
      FROM
        information_schema.columns
      WHERE
        table_name = 'projects'
        AND column_name = 'github_connection_type'
    )
    THEN
      ALTER TABLE projects
      ADD COLUMN github_connection_type VARCHAR(50) DEFAULT 'https';
    END IF;

    -- Add github_ssh_key_id if not exists
    IF NOT EXISTS (
      SELECT
        1
      FROM
        information_schema.columns
      WHERE
        table_name = 'projects'
        AND column_name = 'github_ssh_key_id'
    )
    THEN
      ALTER TABLE projects
      ADD COLUMN github_ssh_key_id UUID REFERENCES ssh_keys(id);
    END IF;

    -- Add github_cli_token if not exists
    IF NOT EXISTS (
      SELECT
        1
      FROM
        information_schema.columns
      WHERE
        table_name = 'projects'
        AND column_name = 'github_cli_token'
    )
    THEN
      ALTER TABLE projects
      ADD COLUMN github_cli_token VARCHAR(500);
    END IF;
  END $ $;

  -- Create SSH keys table
  CREATE TABLE
  IF
    NOT EXISTS ssh_keys (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid()
      , user_id UUID NOT NULL REFERENCES users(id)
      ON DELETE CASCADE
      , name VARCHAR(255) NOT NULL
      , public_key TEXT NOT NULL
      , private_key TEXT NOT NULL
      , key_fingerprint VARCHAR(255) UNIQUE NOT NULL
      , github_username VARCHAR(255)
      , is_active BOOLEAN DEFAULT TRUE
      , created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      , updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      , last_used_at TIMESTAMP WITH TIME ZONE
      , CONSTRAINT ssh_keys_user_id_name_key UNIQUE (user_id, name)
    );

    -- Create indexes for SSH keys
    CREATE INDEX
    IF
      NOT EXISTS idx_ssh_keys_user_id
      ON ssh_keys(user_id);
      CREATE INDEX
      IF
        NOT EXISTS idx_ssh_keys_fingerprint
        ON ssh_keys(key_fingerprint);
        CREATE INDEX
        IF
          NOT EXISTS idx_ssh_keys_github_username
          ON ssh_keys(github_username);

          -- Update trigger for SSH keys updated_at
          CREATE OR REPLACE FUNCTION update_ssh_keys_updated_at()
          RETURNS TRIGGER AS $ $
          BEGIN
            NEW.updated_at = NOW();
            RETURN
            NEW;
          END;
          $ $
          LANGUAGE plpgsql;

          CREATE TRIGGER trigger_update_ssh_keys_updated_at
          BEFORE UPDATE
          ON ssh_keys
          FOR EACH ROW EXECUTE FUNCTION update_ssh_keys_updated_at();