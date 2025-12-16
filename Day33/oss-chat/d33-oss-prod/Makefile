NAMESPACE ?= d33-oss-prod

.PHONY: ns deploy verify rollback cleanup

ns:
	./scripts/10_create_namespace.sh

deploy:
	./scripts/20_deploy_all.sh

verify:
	./scripts/30_verify.sh

rollback:
	./scripts/40_rollback.sh

cleanup:
	./scripts/90_cleanup.sh
