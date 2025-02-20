FROM postgres:14

# Copy initialization scripts
COPY init/ /docker-entrypoint-initdb.d/

# Set default environment variables
ENV POSTGRES_DB=student_registration_backup
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres