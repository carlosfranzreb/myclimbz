PROD_DB_FILE=$1
BACKUP_DIR=$2
MONTH_NR=$(date +%m)

mkdir -p $BACKUP_DIR
sqlite3 $PROD_DB_FILE  ".backup '$BACKUP_DIR/prod_$MONTH_NR.db'"