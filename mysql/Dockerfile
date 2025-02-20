FROM mysql:8.0

# Copy custom configuration and set proper permissions
COPY conf.d/my.cnf /etc/mysql/conf.d/
RUN chown root:root /etc/mysql/conf.d/my.cnf && \
    chmod 644 /etc/mysql/conf.d/my.cnf

# Copy initialization scripts
COPY init/ /docker-entrypoint-initdb.d/

# Set required MySQL environment variables
ENV MYSQL_DATABASE=student_registration
ENV MYSQL_USER=user
ENV MYSQL_PASSWORD=password
ENV MYSQL_ROOT_PASSWORD=rootpassword